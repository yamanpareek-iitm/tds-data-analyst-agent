import io, base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WIKI_URL = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"

def _fetch_table():
    # Simple robust read of the page’s tables; pick the one with Rank and Peak
    dfs = pd.read_html(WIKI_URL)
    target = None
    for df in dfs:
        cols = [str(c).strip().lower() for c in df.columns]
        if "rank" in cols and "peak" in cols:
            target = df
            break
    if target is None:
        for df in dfs:
            cols = [str(c).strip().lower() for c in df.columns]
            if "rank" in cols:
                target = df
                break
    if target is None:
        target = dfs[0]
    return target

def _clean_numeric(series):
    return pd.to_numeric(series.astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")

def _png_base64(fig, max_bytes=100_000):
    for dpi in [110, 100, 90, 80, 70, 60, 50]:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1, metadata={"Software":"matplotlib"})
        b = buf.getvalue()
        if len(b) <= max_bytes:
            plt.close(fig)
            return base64.b64encode(b).decode("ascii")
    plt.close(fig)
    return base64.b64encode(b).decode("ascii")

def handle_films_task() -> list[str]:
    df = _fetch_table()
    df.columns = [str(c).strip() for c in df.columns]

    def find_col(options):
        for c in df.columns:
            lc = c.lower()
            for o in options:
                if o in lc:
                    return c
        return None

    col_title = find_col(["title"])
    col_year = find_col(["year"])
    col_gross = find_col(["worldwide", "gross"])
    col_peak = find_col(["peak"])
    col_rank = find_col(["rank"])

    if col_year:
        df[col_year] = pd.to_numeric(df[col_year], errors="coerce")
    if col_gross:
        df[col_gross] = _clean_numeric(df[col_gross])
    if col_peak:
        df[col_peak] = pd.to_numeric(df[col_peak], errors="coerce")
    if col_rank:
        df[col_rank] = pd.to_numeric(df[col_rank], errors="coerce")

    # 1) $2bn before 2000
    a1 = ""
    if col_gross and col_year:
        a1 = str(int(((df[col_gross] >= 2_000_000_000) & (df[col_year] < 2000)).sum()))

    # 2) earliest > $1.5bn
    a2 = ""
    if col_gross and col_year and col_title:
        over = df[df[col_gross] > 1_500_000_000].dropna(subset=[col_year])
        if not over.empty:
            row = over.sort_values(col_year, ascending=True).iloc[0]
            a2 = str(row[col_title])

    # 3) correlation Rank vs Peak
    a3 = ""
    if col_rank and col_peak:
        sub = df.dropna(subset=[col_rank, col_peak]).copy()
        if not sub.empty:
            corr = float(sub[col_rank].astype(float).corr(sub[col_peak].astype(float)))
            a3 = f"{corr:.6f}"

    # 4) scatter plot with dotted red regression
    a4 = ""
    if col_rank and col_peak:
        sub = df.dropna(subset=[col_rank, col_peak]).copy()
        x = sub[col_rank].astype(float).values
        y = sub[col_peak].astype(float).values
        if len(x) >= 2:
            fig, ax = plt.subplots(figsize=(4,3))
            ax.scatter(x, y, s=14, alpha=0.9)
            b, a = np.polyfit(x, y, 1)
            xs = np.linspace(float(np.min(x)), float(np.max(x)), 200)
            ax.plot(xs, a + b*xs, "r--", linewidth=1.8)
            ax.set_xlabel("Rank")
            ax.set_ylabel("Peak")
            ax.set_title("Rank vs Peak")
            b64 = _png_base64(fig, max_bytes=100_000)
            a4 = f"data:image/png;base64,{b64}"

    return [a1, a2, a3, a4]
