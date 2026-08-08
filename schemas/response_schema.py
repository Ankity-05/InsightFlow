"""Final structured response to the frontend."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FinalResponse(BaseModel):
    """Guaranteed structured output delivered to the user interface."""
    answer: str = Field(description="Natural language answer to the user's question")
    sql_used: Optional[str] = Field(default=None, description="SQL query that was executed")
    chart_data: Optional[Dict[str, Any]] = Field(default=None, description="Plotly JSON figure if applicable")
    chart_config: Optional[Dict[str, Any]] = Field(default=None, description="Chart configuration metadata")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in the answer")
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested next queries the user might ask"
    )
    warnings: List[str] = Field(default_factory=list, description="Caveats or data quality notes")
    execution_time_ms: Optional[int] = Field(default=None, description="Total pipeline execution time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional trace info")
