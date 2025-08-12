import os
import json
from typing import Dict, Any, List

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

SYSTEM_PROMPT = """You generate Python-only steps to solve data analysis tasks from a question and optional files.
Rules:
- Use only pandas, numpy, matplotlib (Agg), and builtins.
- Access uploaded files via context['files'][filename] exact paths.
- Access parsed YAML via context['yaml_data']={'files':{name:obj},'__summary__':{...}}.
- If the task references a URL table, you may use pandas.read_html(url). If lxml is unavailable, flavor='html5lib' can be used if installed.
- Always label plot axes and title; produce base64 PNG with png_base64(fig, max_bytes).
- Do not print or write files; set final payload to RESULT (dict or list) matching requested format.
- Do not produce YAML yourself; server handles serialization if needed.
- Optimize for <3 minutes total execution.
"""

def build_user_prompt(qtext: str, data_spec: Dict[str, Any], output_spec: Dict[str, Any]) -> str:
    return json.dumps({
        "question": qtext,
        "data_spec": data_spec,
        "output_spec": output_spec,
        "context_contract": {
            "files": "dict[str filename] -> absolute path",
            "yaml_data": "{'files': {filename: python_obj}, '__summary__': {...}}",
            "helpers": ["png_base64(fig, max_bytes)", "assert_image_under_limit(b64, max_bytes)"]
        }
    }, ensure_ascii=False)

async def plan_with_llm(qtext: str, data_spec: Dict[str, Any], output_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Replace this stub with a real LLM call in production.
    user = build_user_prompt(qtext, data_spec, output_spec)

    code = f"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

files = context["files"]
yaml_data = context.get("yaml_data", {{}})

csv_paths = [files[k] for k in files if k.lower().endswith(".csv")]
payload = None

if csv_paths:
    df = pd.read_csv(csv_paths[0])
    summary = {{"columns": list(df.columns), "rows": int(len(df))}}
    num = df.select_dtypes(include=[np.number])
    if not num.empty:
        summary["numeric_columns"] = list(num.columns)
        summary["means"] = {{c: float(num[c].mean()) for c in num.columns}}
        fig, ax = plt.subplots(figsize=(4,3))
        ax.plot(list(summary["means"].keys()), list(summary["means"].values()), color="red")
        ax.set_xlabel("Column")
        ax.set_ylabel("Mean")
        ax.set_title("Numeric Column Means")
        b64 = png_base64(fig, max_bytes=100000)
        assert_image_under_limit(b64, 100000)
        payload = {{"summary": summary, "plot": b64}}
    else:
        payload = {{"summary": summary}}
else:
    yfiles = yaml_data.get("files", {{}})
    merged = {{}}
    for fname, obj in yfiles.items():
        if isinstance(obj, dict):
            for k,v in obj.items():
                merged.setdefault(k, v)
    payload = {{"yaml_summary": yaml_data.get("__summary__", {{}}), "yaml_merged_keys": list(merged.keys())}}

as_array = {str(output_spec.get("type") == "json_array")}
if as_array:
    items = []
    if "summary" in payload:
        items.append(str(payload["summary"].get("rows","")))
        items.append(",".join(payload["summary"].get("columns",[])))
    elif "yaml_summary" in payload:
        items.append(str(payload["yaml_summary"].get("count","")))
        items.append(",".join(payload.get("yaml_merged_keys",[])))
    if not items:
        items = ["",""]
    RESULT = [str(x) for x in items]
else:
    RESULT = payload
"""
    return [{"type": "python", "code": code}]
