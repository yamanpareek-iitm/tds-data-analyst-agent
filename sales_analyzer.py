import pandas as pd
import numpy as np
from plot_utils import png_base64_under_limit

def handle_sales_task(qtext: str, csv_path: str) -> dict:
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna(subset=["date", "region", "sales"])

    total_sales = float(df["sales"].sum())
    by_region = df.groupby("region")["sales"].sum().sort_values(ascending=False)
    top_region = str(by_region.index[0]) if len(by_region) else ""

    df["day"] = df["date"].dt.day
    day_sales_correlation = float(df["day"].corr(df["sales"]))

    # Blue bar chart
    bar_fig = by_region.plot(kind="bar", color="blue", title="Total Sales by Region").get_figure()
    ax1 = bar_fig.axes[0]
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Total Sales")
    bar_b64 = png_base64_under_limit(bar_fig)

    median_sales = float(df["sales"].median())
    total_sales_tax = float(round(total_sales * 0.10))

    # Red cumulative line chart
    s = df.sort_values("date").copy()
    s["cumulative_sales"] = s["sales"].cumsum()
    import matplotlib.pyplot as plt
    fig2, ax2 = plt.subplots(figsize=(4,3))
    ax2.plot(s["date"], s["cumulative_sales"], color="red")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Cumulative Sales")
    ax2.set_title("Cumulative Sales Over Time")
    line_b64 = png_base64_under_limit(fig2)

    return {
        "total_sales": total_sales,
        "top_region": top_region,
        "day_sales_correlation": day_sales_correlation,
        "bar_chart": bar_b64,
        "median_sales": median_sales,
        "total_sales_tax": total_sales_tax,
        "cumulative_sales_chart": line_b64,
    }
