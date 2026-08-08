"""Parallel validation chain using RunnableParallel."""
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from tools.security_tools import validate_sql
from tools.sql_tools import get_table_schema

def build_validation_chain():
    """Build parallel validation chain.

    Runs syntax, permission, and injection checks in parallel.
    """
    def syntax_check(inputs):
        query = inputs.get("query", "")
        result = validate_sql.invoke({"query": query, "user_role": inputs.get("user_role", "viewer")})
        return result

    def schema_check(inputs):
        tables = inputs.get("tables_used", [])
        schemas = {}
        for table in tables:
            schemas[table] = get_table_schema.invoke({"table_name": table})
        return schemas

    # For demo without full async, we use a simple sequential wrapper
    def validation_wrapper(inputs):
        syntax_result = syntax_check(inputs)
        schema_result = schema_check(inputs)
        return {
            "validation": syntax_result,
            "schemas": schema_result,
            "query": inputs.get("query"),
            "user_role": inputs.get("user_role", "viewer")
        }

    return validation_wrapper
