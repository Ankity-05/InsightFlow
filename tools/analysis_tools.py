"""Statistical analysis and anomaly detection tools."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from langchain_core.tools import tool
from schemas import AnalysisResult

@tool
def calculate_statistics(data_json: List[Dict[str, Any]], column: str) -> Dict[str, Any]:
    """Calculate descriptive statistics for a numeric column.

    Args:
        data_json: List of row dictionaries (from SQL query result).
        column: Column name to analyze.

    Returns:
        Dictionary with mean, median, std, min, max, and percentiles.
    """
    try:
        df = pd.DataFrame(data_json)
        if column not in df.columns:
            return {"error": f"Column '{column}' not found in data."}

        series = pd.to_numeric(df[column], errors="coerce").dropna()

        if len(series) == 0:
            return {"error": f"Column '{column}' has no numeric data."}

        stats = {
            "count": int(series.count()),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "std": round(float(series.std()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "q25": round(float(series.quantile(0.25)), 2),
            "q75": round(float(float(series.quantile(0.75))), 2),
        }

        # Auto-insights
        insights = []
        cv = stats["std"] / stats["mean"] if stats["mean"] != 0 else 0
        if cv > 0.5:
            insights.append(f"High variability detected (CV={cv:.2f}).")
        if stats["mean"] > stats["median"] * 1.2:
            insights.append("Right-skewed distribution: mean > median.")
        elif stats["median"] > stats["mean"] * 1.2:
            insights.append("Left-skewed distribution: median > mean.")

        return AnalysisResult(
            metric=f"descriptive_stats_{column}",
            value=stats["mean"],
            details=stats,
            insights=insights,
            anomalies=[]
        ).model_dump()
    except Exception as e:
        return {"error": str(e)}

@tool
def anomaly_detector(data_json: List[Dict[str, Any]], column: str, 
                     method: str = "iqr", threshold: float = 1.5) -> Dict[str, Any]:
    """Detect anomalies in a numeric column using IQR or Z-score.

    Args:
        data_json: List of row dictionaries.
        column: Column name to analyze.
        method: 'iqr' or 'zscore'.
        threshold: Threshold for anomaly detection (default 1.5 for IQR, 3.0 for Z-score).

    Returns:
        Dictionary with anomaly count, indices, and flagged rows.
    """
    try:
        df = pd.DataFrame(data_json)
        if column not in df.columns:
            return {"error": f"Column '{column}' not found."}

        series = pd.to_numeric(df[column], errors="coerce").dropna()
        anomalies = []

        if method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
            mask = (series < lower) | (series > upper)
        elif method == "zscore":
            mean, std = series.mean(), series.std()
            if std == 0:
                return {"anomaly_count": 0, "anomalies": [], "method": "zscore"}
            z_scores = np.abs((series - mean) / std)
            mask = z_scores > threshold
        else:
            return {"error": "Method must be 'iqr' or 'zscore'."}

        anomaly_rows = df[mask].to_dict(orient="records")
        for idx, row in enumerate(anomaly_rows):
            anomalies.append({
                "row_index": int(series[mask].index[idx]),
                "value": row.get(column),
                "reason": f"Exceeds {method.upper()} threshold"
            })

        insights = []
        if len(anomalies) > 0:
            pct = len(anomalies) / len(series) * 100
            insights.append(f"{len(anomalies)} anomalies detected ({pct:.1f}% of data).")
        else:
            insights.append("No significant anomalies detected.")

        return AnalysisResult(
            metric=f"anomaly_detection_{column}",
            value=len(anomalies),
            details={"method": method, "threshold": threshold, "total_rows": len(series)},
            insights=insights,
            anomalies=anomalies
        ).model_dump()
    except Exception as e:
        return {"error": str(e)}
