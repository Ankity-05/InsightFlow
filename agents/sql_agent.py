"""SQL execution agent using LangGraph ReAct pattern."""
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.sql_tools import execute_sql_query, get_table_schema, get_table_names
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

def build_sql_agent():
    """Build a ReAct agent specialized in SQL execution and schema discovery.

    Uses LangGraph's create_react_agent for robust multi-step reasoning.
    """
    if not OPENAI_API_KEY:
        return None

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=OPENAI_API_KEY
    )

    tools = [execute_sql_query, get_table_schema, get_table_names]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier="""You are an expert SQL database agent. Your job is to:
1. Understand the user's data question
2. Discover the relevant tables and schemas
3. Write and execute correct SQLite queries
4. Return clean, accurate results

Always verify table schemas before writing queries. Use LIMIT clauses."""
    )

    return agent
