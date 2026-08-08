"""Structured user intent extraction."""
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class UserIntent(BaseModel):
    """Structured understanding of a natural language query."""
    intent_type: Literal["aggregation", "comparison", "trend", "lookup", "anomaly", "unknown"] = Field(
        description="The analytical intent of the query"
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Named entities: tables, columns, metrics, product names, regions"
    )
    time_range: Optional[str] = Field(
        default=None,
        description="Temporal filters mentioned (e.g., 'Q2 2024', 'last 30 days')"
    )
    requires_chart: bool = Field(
        default=False,
        description="Whether a visualization would help answer this query"
    )
    ambiguity_flags: List[str] = Field(
        default_factory=list,
        description="List of ambiguous terms that need clarification"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0, le=1.0,
        description="Confidence score of intent extraction"
    )
