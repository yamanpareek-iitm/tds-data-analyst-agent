import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from plot_utils import png_base64_under_limit

def handle_weather_task(qtext: str, csv_path: str) -> dict:
    # Load CSV with date, temperature_c, precip_mm columns
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="coerce")
    df["precip_mm"] = pd.to_numeric(df["precip_mm"], errors="coerce")
    df = df.dropna(subset=["date", "temperature_c", "precip_mm"])

    # 1. Average temp
    average_temp_c = float(np.mean(df["temperature_c"])) if not df.empty else 0.0

    # 2. Date of max precip
    max_precip_date = ""
    if not df.empty:
        idx = df["precip_mm"].idxmax()
        date_val = df.loc[idx, "date"]
        max_precip_date = (
            date_val.strftime("%Y-%m-%d") if pd.notnull(date_val) else ""
        )

    # 3. Min temperature
    min_temp_c = int(np.min(df["temperature_c"])) if not df.empty else 0

    # 4. Correlation between temp & precip
    temp_precip_correlation = float(df["temperature_c"].corr(df["precip_mm"])) if not df.empty else 0.0

    # 5. Average precip
    average_precip_mm = float(np.mean(df["precip_mm"])) if not df.empty else 0.0

    # 6. Temperature over time: line chart, red line, labeled
    fig1, ax1 = plt.subplots(figsize=(4,3))
    ax1.plot(df["date"], df["temperature_c"], color="red", linewidth=2)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("Temperature Over Time")
    plt.tight_layout()
    temp_chart_b64 = png_base64_under_limit(fig1)

    # 7. Precip histogram, orange bars, labeled
    fig2, ax2 = plt.subplots(figsize=(4,3))
    ax2.hist(df["precip_mm"], color="orange", bins=min(10, len(df)))
    ax2.set_xlabel("Precipitation (mm)")
    ax2.set_ylabel("Count")
    ax2.set_title("Precipitation Histogram")
    plt.tight_layout()
    precip_chart_b64 = png_base64_under_limit(fig2)

    return {
        "average_temp_c": average_temp_c,
        "max_precip_date": max_precip_date,
        "min_temp_c": min_temp_c,
        "temp_precip_correlation": temp_precip_correlation,
        "average_precip_mm": average_precip_mm,
        "temp_line_chart": temp_chart_b64,
        "precip_histogram": precip_chart_b64,
    }
