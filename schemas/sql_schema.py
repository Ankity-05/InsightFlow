"""Structured SQL query and validation schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional

class SQLQuery(BaseModel):
    """Generated SQL query with metadata."""
    query: str = Field(description="The generated SQL SELECT statement")
    explanation: str = Field(description="Plain-English explanation of what the query does")
    estimated_rows: Optional[int] = Field(default=None, description="Estimated number of result rows")
    tables_used: List[str] = Field(default_factory=list, description="Tables referenced in the query")

class SQLValidation(BaseModel):
    """Validation results for a SQL query."""
    is_valid: bool = Field(description="Whether the SQL passed all checks")
    syntax_ok: bool = Field(default=True)
    no_forbidden_ops: bool = Field(default=True)
    no_injection_risk: bool = Field(default=True)
    within_row_limit: bool = Field(default=True)
    pii_safe: bool = Field(default=True)
    errors: List[str] = Field(default_factory=list, description="List of validation failures")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking concerns")
    requires_approval: bool = Field(default=False, description="Whether human approval is needed")
    approval_reason: Optional[str] = Field(default=None, description="Why approval is required")
