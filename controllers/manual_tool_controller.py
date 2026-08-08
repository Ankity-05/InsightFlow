"""Manual tool calling with business logic gates."""
from typing import Dict, Any, List, Optional
from langchain_core.messages import AIMessage, ToolMessage
from config import ROLE_PERMISSIONS, MAX_ROWS_HARD_LIMIT

class ManualToolController:
    """Controls tool execution with conditional logic, permissions, and safety gates."""

    def __init__(self, user_role: str = "viewer"):
        self.user_role = user_role
        self.approved_tools = ROLE_PERMISSIONS.get(user_role, [])
        self.execution_log: List[Dict[str, Any]] = []

    def execute_tool_calls(self, ai_message: AIMessage, tool_map: Dict[str, Any]) -> List[ToolMessage]:
        """Execute tool calls with full business logic gates.

        Args:
            ai_message: The AI message containing tool_calls.
            tool_map: Dictionary mapping tool names to callable tools.

        Returns:
            List of ToolMessage results.
        """
        tool_results = []

        for tool_call in ai_message.tool_calls:
            tool_name = tool_call.get("name")
            args = tool_call.get("args", {})
            call_id = tool_call.get("id", "unknown")

            # i. Permission check
            if tool_name not in self.approved_tools:
                result = f"ACCESS DENIED: Tool '{tool_name}' is not approved for role '{self.user_role}'."
                tool_results.append(ToolMessage(content=result, tool_call_id=call_id))
                self.execution_log.append({"tool": tool_name, "status": "denied", "reason": "role_permission"})
                continue

            # ii. Custom business logic for SQL
            if tool_name == "execute_sql_query":
                query = args.get("query", "")
                query_upper = query.upper()

                # Destructive operation check
                if any(kw in query_upper for kw in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
                    result = "BLOCKED: Destructive operations require admin MFA approval."
                    tool_results.append(ToolMessage(content=result, tool_call_id=call_id))
                    self.execution_log.append({"tool": tool_name, "status": "blocked", "reason": "destructive_op"})
                    continue

                # Row limit enforcement
                max_rows = args.get("max_rows", 1000)
                if max_rows > MAX_ROWS_HARD_LIMIT:
                    args["max_rows"] = MAX_ROWS_HARD_LIMIT

                # PII redaction hint
                if any(pii in query.lower() for pii in ["email", "phone", "address"]):
                    args["_pii_warning"] = "Query may access PII - results will be audited."

            # iii. Execute with error handling
            try:
                tool_func = tool_map.get(tool_name)
                if tool_func is None:
                    raise ValueError(f"Tool '{tool_name}' not found in tool map.")

                output = tool_func.invoke(args)
                tool_results.append(ToolMessage(content=str(output), tool_call_id=call_id))
                self.execution_log.append({"tool": tool_name, "status": "success", "output_preview": str(output)[:200]})
            except Exception as e:
                error_msg = f"Execution failed safely: {str(e)}. Try refining your query."
                tool_results.append(ToolMessage(content=error_msg, tool_call_id=call_id))
                self.execution_log.append({"tool": tool_name, "status": "error", "reason": str(e)})

        return tool_results

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Return the execution audit log."""
        return self.execution_log
