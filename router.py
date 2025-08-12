import re
import pandas as pd

def decide_route(qtext: str, file_map: dict):
    text = (qtext or "").lower()

    # Detect sales CSV based on file name or content
    for name, path in file_map.items():
        if name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(path, nrows=5)
                cols = [c.lower() for c in df.columns]
            except Exception:
                cols = []

            if "region" in cols and "sales" in cols:
                return {"type": "sales", "csv_path": path}
            
            if "sales" in name.lower():
                return {"type": "sales", "csv_path": path}

    # Detect films task (question content)
    if ("highest grossing films" in text) and \
       ("wikipedia.org/wiki/list_of_highest-grossing_films" in text):
        return {"type": "films"}

    # Detect network CSV
    for name, path in file_map.items():
        if name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(path, nrows=2)
                cols = list(df.columns)
            except Exception:
                cols = []

            if len(cols) == 2 and all(isinstance(c, str) for c in cols):
                # Likely an edge list
                if "edge" in name.lower() or "node" in name.lower():
                    return {"type": "network", "csv_path": path}
                # Also detect by typical node names
                if df.dtypes.nunique() == 1 and df.dtypes.iloc[0] == 'object':
                    return {"type": "network", "csv_path": path}

    # Detect weather CSV
    for name, path in file_map.items():
        if name.lower().endswith(".csv"):
            try:
                df = pd.read_csv(path, nrows=5)
                cols = [c.lower() for c in df.columns]
            except Exception:
                cols = []
            
            if any("temp" in c for c in cols) or any("precip" in c for c in cols):
                return {"type": "weather", "csv_path": path}
            if "weather" in name.lower():
                return {"type": "weather", "csv_path": path}

    # Default: generic LLM pipeline
    return {"type": "llm"}

def detect_output_spec(qtext: str):
    text = (qtext or "").lower()
    spec = {"type": "json_object", "keys": None,
            "image_constraints": {"max_png_bytes": 100_000}}

    if "respond with a json array" in text or "return a json array" in text:
        spec["type"] = "json_array"
    if "respond with a json object" in text or "return a json object" in text:
        spec["type"] = "json_object"

    # Extract explicit keys from text if present
    keys = re.findall(r'"([A-Za-z0-9_\-\s#]+)"\s*:', qtext)
    if keys:
        spec["keys"] = keys

    # Detect image byte limit
    m = re.search(r'under\s+(\d{2,6})\s*bytes', text)
    if m:
        try:
            spec["image_constraints"]["max_png_bytes"] = int(m.group(1))
        except:
            pass

    return spec
