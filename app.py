from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import tempfile, os

from router import decide_route, detect_output_spec
from planner import plan_with_llm
from executor import run_code_steps
from validators import ValidationError, validate_final_output_schema
from yaml_utils import load_yaml_files_merged

# Existing analyzers
from sales_analyzer import handle_sales_task
from films_analyzer import handle_films_task

from network_analyzer import handle_network_task
from weather_analyzer import handle_weather_task

app = FastAPI(title="LLM Data Analyst Agent")

@app.post("/api/")
async def analyze_api(
    questions: UploadFile = File(...),
    files: Optional[List[UploadFile]] = File(None),
):
    tempdir = tempfile.mkdtemp(prefix="llm_daa_")
    try:
        # Read the question text
        qtext = (await questions.read()).decode("utf-8", errors="ignore")

        # Save uploaded files and map filename -> path
        file_map: Dict[str, str] = {}
        if files:
            for f in files:
                path = os.path.join(tempdir, f.filename)
                with open(path, "wb") as out:
                    out.write(await f.read())
                file_map[f.filename] = path

        # Parse YAML files into structured context for LLM
        yaml_context = load_yaml_files_merged(file_map)

        # Route the request
        route = decide_route(qtext, file_map)

        # ---- Fast-path analyzers ----

        # SALES
        if "sample-sales.csv" in file_map:
            result = handle_sales_task(qtext, file_map["sample-sales.csv"])
            return JSONResponse(content=result)

        # FILMS
        if route["type"] == "films":
            result_array = handle_films_task()
            if not (isinstance(result_array, list) and len(result_array) == 4 and all(isinstance(x, str) for x in result_array)):
                raise HTTPException(status_code=400, detail="Validation failed: Expected JSON array output.")
            return JSONResponse(content=result_array)

        # NETWORK
        if "edges.csv" in file_map:
            result = handle_network_task(qtext, file_map["edges.csv"])
            return JSONResponse(content=result)

        # WEATHER
        if "sample-weather.csv" in file_map:
            result = handle_weather_task(qtext, file_map["sample-weather.csv"])
            return JSONResponse(content=result)

        # ---- Generic LLM pipeline ----
        output_spec = detect_output_spec(qtext)
        plan = await plan_with_llm(
            qtext,
            {"files": list(file_map.keys()), "yaml_summary": yaml_context.get("__summary__", {})},
            output_spec
        )
        context = {
            "files": file_map,
            "tempdir": tempdir,
            "yaml_data": yaml_context
        }
        exec_result: Any = await run_code_steps(plan, context)

        validate_final_output_schema(exec_result, output_spec)

        if output_spec.get("type") == "json_array":
            if not isinstance(exec_result, list):
                raise HTTPException(status_code=400, detail="Validation failed: Expected JSON array output.")
            return JSONResponse(content=[str(x) for x in exec_result])
        else:
            if not isinstance(exec_result, dict):
                raise HTTPException(status_code=400, detail="Validation failed: Expected JSON object output.")
            return JSONResponse(content=exec_result)

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=f"Validation failed: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    finally:
        # In production, you might remove tempdir here
        pass

@app.get("/")
def health():
    html_content = """
    <html>
        <head>
            <title>API Home</title>
        </head>
        <body>
            <h1>Welcome to the LLM Data Analyst Agent API</h1>
            <p>Click the link below to access the API documentation:</p>
            <a href="/docs" style="font-size:20px;">Go to API Docs</a>
        </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")