"""Structured analysis and visualization schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class ChartConfig(BaseModel):
    """Configuration for generating a chart."""
    chart_type: Literal["bar", "line", "pie", "scatter", "histogram", "table"] = Field(
        description="Type of chart to generate"
    )
    x_column: str = Field(description="Column to use for X-axis / categories")
    y_column: Optional[str] = Field(default=None, description="Column to use for Y-axis / values")
    title: str = Field(default="Chart", description="Chart title")
    color_column: Optional[str] = Field(default=None, description="Optional column for color grouping")

class AnalysisResult(BaseModel):
    """Result from statistical analysis."""
    metric: str = Field(description="Name of the analysis performed")
    value: Any = Field(description="Primary result value")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional statistics")
    insights: List[str] = Field(default_factory=list, description="Auto-generated insights")
    anomalies: List[Dict[str, Any]] = Field(default_factory=list, description="Detected anomalies")
