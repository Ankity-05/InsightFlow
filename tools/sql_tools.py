"""SQL execution and schema discovery tools."""
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from config import DB_PATH, MAX_ROWS_DEFAULT, MAX_ROWS_HARD_LIMIT, FORBIDDEN_KEYWORDS

@tool
def execute_sql_query(query: str, max_rows: int = MAX_ROWS_DEFAULT) -> Dict[str, Any]:
    """Execute a read-only SQL query against the SQLite database.

    Args:
        query: A valid SQL SELECT statement.
        max_rows: Maximum rows to return (default 1000, hard limit 10000).

    Returns:
        Dictionary with columns, rows, row_count, and execution metadata.
    """
    # Enforce hard limit
    max_rows = min(max_rows, MAX_ROWS_HARD_LIMIT)

    # Safety: block destructive operations
    query_upper = query.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            return {
                "success": False,
                "error": f"Destructive operation detected: '{keyword}' is not allowed.",
                "columns": [], "rows": [], "row_count": 0
            }

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("PRAGMA query_only = ON")  # Read-only mode at connection level

        # Add LIMIT if not present
        if "LIMIT" not in query_upper:
            query = query.rstrip(";
 ") + f" LIMIT {max_rows}"

        df = pd.read_sql_query(query, conn)
        conn.close()

        rows = df.to_dict(orient="records")
        return {
            "success": True,
            "columns": list(df.columns),
            "rows": rows,
            "row_count": len(rows),
            "query": query
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "columns": [], "rows": [], "row_count": 0
        }

@tool
def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Retrieve the schema (columns and types) for a given table.

    Args:
        table_name: Name of the table to describe.

    Returns:
        Dictionary with table_name, columns list, and sample data.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [
            {"name": row[1], "type": row[2], "not_null": bool(row[3]), "default": row[4]}
            for row in cursor.fetchall()
        ]

        # Get sample rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample_rows = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor.fetchall()]

        conn.close()
        return {
            "table_name": table_name,
            "columns": columns,
            "sample_rows": sample_rows
        }
    except Exception as e:
        return {"error": str(e), "table_name": table_name, "columns": [], "sample_rows": []}

@tool
def get_table_names() -> List[str]:
    """List all available tables in the database.

    Returns:
        List of table names.
    """
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        return [f"Error: {e}"]
