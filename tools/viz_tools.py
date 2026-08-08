"""Visualization and chart generation tools."""
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from schemas import ChartConfig

@tool
def generate_chart(data_json: List[Dict[str, Any]], chart_type: str, 
                   x_column: str, y_column: Optional[str] = None,
                   title: str = "Chart", color_column: Optional[str] = None) -> Dict[str, Any]:
    """Generate a Plotly chart from query result data.

    Args:
        data_json: List of row dictionaries from SQL query.
        chart_type: Type of chart ('bar', 'line', 'pie', 'scatter', 'histogram').
        x_column: Column for X-axis / categories.
        y_column: Column for Y-axis / values (not needed for histogram).
        title: Chart title.
        color_column: Optional column for color grouping.

    Returns:
        Dictionary with Plotly JSON figure and metadata.
    """
    try:
        import pandas as pd
        df = pd.DataFrame(data_json)

        if chart_type == "bar":
            fig = px.bar(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type == "line":
            fig = px.line(df, x=x_column, y=y_column, color=color_column, title=title, markers=True)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_column, values=y_column, title=title)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_column, color=color_column, title=title)
        elif chart_type == "table":
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns), fill_color="paleturquoise", align="left"),
                cells=dict(values=[df[col] for col in df.columns], fill_color="lavender", align="left")
            )])
            fig.update_layout(title=title)
        else:
            return {"error": f"Unsupported chart type: {chart_type}"}

        fig.update_layout(template="plotly_white", height=500)
        chart_json = json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

        return {
            "success": True,
            "chart_json": chart_json,
            "chart_type": chart_type,
            "title": title
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def create_dashboard(data_json: List[Dict[str, Any]], charts_config: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a multi-chart dashboard from data.

    Args:
        data_json: List of row dictionaries.
        charts_config: List of chart configuration dicts.

    Returns:
        Dictionary with multiple chart JSONs.
    """
    charts = []
    for cfg in charts_config:
        result = generate_chart.invoke({
            "data_json": data_json,
            **{k: v for k, v in cfg.items() if k != "data_json"}
        })
        charts.append(result)
    return {"charts": charts, "count": len(charts)}
