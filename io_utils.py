import pandas as pd
from typing import Dict

def load_first_csv(file_map: Dict[str, str]):
    for name, path in file_map.items():
        if name.lower().endswith(".csv"):
            return pd.read_csv(path)
    return None
