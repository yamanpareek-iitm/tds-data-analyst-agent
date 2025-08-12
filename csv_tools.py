import re
import pandas as pd
import numpy as np
from typing import Dict, Optional
from plot_utils import fig_to_base64_under_limit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def maybe_answer_with_builtins(qtext: str, file_map: Dict[str, str]) -> Optional[dict]:
    """
    If questions are generic (e.g., column list, row count, simple correlations/plots),
    answer without LLM for speed and determinism.
    """
    text = (qtext or "").lower()
    wants_array = "respond with a json array" in text or "return a json array" in text

    # If any CSV is present and question is generic summary
    csv_path = None
    for name, path in file_map.items():
        if name.lower().endswith(".csv"):
            csv_path = path
            break
    if not csv_path:
        return None

    df = pd.read_csv(csv_path)
    result = {
        "columns": list(df.columns),
        "rows": int(len(df))
    }

    # If numeric, add simple stats
    num = df.select_dtypes(include=[np.number])
    if not num.empty:
        result["numeric_columns"] = list(num.columns)
        result["means"] = {c: float(num[c].mean()) for c in num.columns}

    # If question asks for correlation between two named columns
    m = re.search(r'correlation\s+between\s+([A-Za-z0-9_]+)\s+and\s+([A-Za-z0-9_]+)', text)
    if m and m.group(1) in df.columns and m.group(2) in df.columns:
        s1, s2 = pd.to_numeric(df[m.group(1)], errors="coerce"), pd.to_numeric(df[m.group(2)], errors="coerce")
        corr = float(s1.corr(s2))
        result["correlation"] = corr

    # If question asks for a simple scatter with regression
    if "scatterplot" in text and len(num.columns) >= 2:
        xcol = num.columns[0]
        ycol = num.columns[1]
        s = df.dropna(subset=[xcol, ycol])
        fig, ax = plt.subplots(figsize=(4,3))
        ax.scatter(s[xcol], s[ycol], s=12, alpha=0.8)
        # regression
        if len(s) >= 2:
            coef = np.polyfit(s[xcol], s[ycol], 1)
            xr = np.linspace(s[xcol].min(), s[xcol].max(), 100)
            yr = coef[0]*xr + coef[1]
            ax.plot(xr, yr, 'r--', linewidth=1.5)
        ax.set_xlabel(str(xcol))
        ax.set_ylabel(str(ycol))
        ax.set_title(f"{xcol} vs {ycol}")
        b64 = fig_to_base64_under_limit(fig, max_bytes=100_000, start_dpi=110)
        result["scatter_plot"] = b64

    if wants_array:
        return [result]
    return result
