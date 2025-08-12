import os
from typing import Dict, Any
import yaml

def _safe_load_yaml_path(path: str):
    with open(path, "rb") as f:
        data = f.read()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="ignore")
    return yaml.safe_load(text)

def load_yaml_files_merged(file_map: Dict[str, str]) -> Dict[str, Any]:
    yaml_files = {n: p for n, p in file_map.items() if n.lower().endswith((".yaml", ".yml"))}
    if not yaml_files:
        return {}
    parsed: Dict[str, Any] = {"files": {}}
    top_keys = set()
    for name, path in yaml_files.items():
        try:
            obj = _safe_load_yaml_path(path)
        except Exception:
            obj = {"__error__": f"Failed to parse YAML: {os.path.basename(path)}"}
        parsed["files"][name] = obj
        if isinstance(obj, dict):
            top_keys |= set(obj.keys())
    parsed["__summary__"] = {"count": len(yaml_files), "keys": sorted(list(top_keys))}
    return parsed
