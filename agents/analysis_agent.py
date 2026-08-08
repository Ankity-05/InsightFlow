"""Data analysis agent using LangGraph ReAct pattern."""
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.analysis_tools import calculate_statistics, anomaly_detector
from tools.viz_tools import generate_chart
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

def build_analysis_agent():
    """Build a ReAct agent for statistical analysis and visualization.

    Can calculate statistics, detect anomalies, and generate charts.
    """
    if not OPENAI_API_KEY:
        return None

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=OPENAI_API_KEY
    )

    tools = [calculate_statistics, anomaly_detector, generate_chart]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier="""You are a senior data analyst agent. Your job is to:
1. Analyze query results statistically
2. Detect anomalies and outliers
3. Generate appropriate visualizations
4. Provide data-driven insights

Always verify data before making claims. Use appropriate statistical methods."""
    )

    return agent
