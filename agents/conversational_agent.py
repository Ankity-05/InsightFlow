"""Conversational agent with memory for multi-turn interactions."""
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from tools.sql_tools import execute_sql_query
from tools.viz_tools import generate_chart
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

def build_conversational_agent():
    """Build a conversational agent with memory for follow-up questions.

    Uses CHAT_CONVERSATIONAL_REACT_DESCRIPTION for natural multi-turn dialogue.
    """
    if not OPENAI_API_KEY:
        return None

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=0.3,  # Slightly higher for conversational flow
        api_key=OPENAI_API_KEY
    )

    tools = [execute_sql_query, generate_chart]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent
