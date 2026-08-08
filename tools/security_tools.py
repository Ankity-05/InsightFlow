"""Security validation and permission checking tools."""
import re
from typing import Dict, Any, List
from langchain_core.tools import tool
from config import FORBIDDEN_KEYWORDS, PII_COLUMNS, MAX_ROWS_HARD_LIMIT
from schemas import SQLValidation

@tool
def validate_sql(query: str, user_role: str = "viewer") -> Dict[str, Any]:
    """Validate a SQL query for safety, syntax, and policy compliance.

    Args:
        query: The SQL query string to validate.
        user_role: Role of the user ('admin', 'analyst', 'viewer').

    Returns:
        SQLValidation result as a dictionary.
    """
    errors = []
    warnings = []
    requires_approval = False
    approval_reason = None

    query_upper = query.upper().strip()

    # 1. Check for forbidden keywords
    forbidden_found = [kw for kw in FORBIDDEN_KEYWORDS if kw in query_upper]
    no_forbidden = len(forbidden_found) == 0
    if forbidden_found:
        errors.append(f"Forbidden operations detected: {', '.join(forbidden_found)}")
        requires_approval = True
        approval_reason = "Destructive SQL operations require admin approval"

    # 2. Basic syntax checks
    syntax_ok = query_upper.startswith("SELECT")
    if not syntax_ok:
        errors.append("Only SELECT queries are allowed.")

    # 3. SQL injection pattern checks
    injection_patterns = [
        r";\s*DROP\s+", r";\s*DELETE\s+", r"UNION\s+SELECT",
        r"--", r"/\*", r"OR\s+\d+\s*=\s*\d+"
    ]
    injection_risk = any(re.search(p, query, re.IGNORECASE) for p in injection_patterns)
    no_injection = not injection_risk
    if injection_risk:
        errors.append("Potential SQL injection pattern detected.")
        requires_approval = True
        approval_reason = "Suspicious SQL patterns detected"

    # 4. PII check
    pii_found = [col for col in PII_COLUMNS if col.lower() in query.lower()]
    pii_safe = len(pii_found) == 0
    if pii_found:
        warnings.append(f"Query references potential PII columns: {', '.join(pii_found)}")

    # 5. Row limit check (soft)
    within_limit = True
    limit_match = re.search(r"LIMIT\s+(\d+)", query_upper)
    if limit_match:
        limit_val = int(limit_match.group(1))
        if limit_val > MAX_ROWS_HARD_LIMIT:
            within_limit = False
            warnings.append(f"Row limit {limit_val} exceeds hard cap of {MAX_ROWS_HARD_LIMIT}.")

    is_valid = syntax_ok and no_forbidden and no_injection and within_limit

    # Admin override
    if user_role == "admin" and requires_approval:
        requires_approval = False  # Admin can bypass approval for testing
        approval_reason = None

    return SQLValidation(
        is_valid=is_valid,
        syntax_ok=syntax_ok,
        no_forbidden_ops=no_forbidden,
        no_injection_risk=no_injection,
        within_row_limit=within_limit,
        pii_safe=pii_safe,
        errors=errors,
        warnings=warnings,
        requires_approval=requires_approval,
        approval_reason=approval_reason
    ).model_dump()

@tool
def check_permissions(user_role: str, requested_tool: str) -> Dict[str, Any]:
    """Check if a user role has permission to use a specific tool.

    Args:
        user_role: The user's role.
        requested_tool: Name of the tool being requested.

    Returns:
        Permission check result.
    """
    from config import ROLE_PERMISSIONS
    allowed = ROLE_PERMISSIONS.get(user_role, [])
    has_access = requested_tool in allowed
    return {
        "user_role": user_role,
        "requested_tool": requested_tool,
        "has_access": has_access,
        "allowed_tools": allowed
    }
