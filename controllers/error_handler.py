"""Centralized error handling with user-friendly messages."""
from typing import Dict, Any, Optional
import traceback

class ErrorHandler:
    """Handles errors gracefully with categorized responses and recovery hints."""

    ERROR_CATEGORIES = {
        "sql_syntax": {
            "message": "The generated SQL had a syntax error.",
            "hint": "Try rephrasing your question with clearer table or column names."
        },
        "sql_execution": {
            "message": "The query could not be executed against the database.",
            "hint": "The table or column might not exist. Try asking about available tables first."
        },
        "permission_denied": {
            "message": "You don't have permission to perform this action.",
            "hint": "Contact your admin to request elevated access."
        },
        "rate_limit": {
            "message": "Rate limit exceeded. Please wait a moment.",
            "hint": "Try again in a few seconds."
        },
        "unknown": {
            "message": "An unexpected error occurred.",
            "hint": "Please try again or contact support."
        }
    }

    @classmethod
    def handle(cls, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Categorize and format an error for the user.

        Args:
            exception: The caught exception.
            context: Optional context dict with 'query', 'sql', etc.

        Returns:
            Formatted error response dict.
        """
        error_str = str(exception).lower()
        category = "unknown"

        if "syntax" in error_str or "parse" in error_str or "near" in error_str:
            category = "sql_syntax"
        elif "no such table" in error_str or "no such column" in error_str or "operationalerror" in error_str:
            category = "sql_execution"
        elif "permission" in error_str or "access denied" in error_str or "forbidden" in error_str:
            category = "permission_denied"
        elif "rate limit" in error_str or "too many requests" in error_str:
            category = "rate_limit"

        error_info = cls.ERROR_CATEGORIES.get(category, cls.ERROR_CATEGORIES["unknown"])

        return {
            "success": False,
            "category": category,
            "user_message": error_info["message"],
            "hint": error_info["hint"],
            "technical_detail": str(exception),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }

    @classmethod
    def is_retryable(cls, exception: Exception) -> bool:
        """Determine if an error is worth retrying."""
        error_str = str(exception).lower()
        retryable_patterns = ["rate limit", "timeout", "connection", "temporary"]
        return any(p in error_str for p in retryable_patterns)
