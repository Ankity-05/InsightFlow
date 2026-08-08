"""Final response assembly chain."""
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas import FinalResponse
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

def build_response_chain():
    """Build the final response synthesis chain.

    Takes query results, analysis, and chart data to produce a structured FinalResponse.
    """
    if not OPENAI_API_KEY:
        def mock_response(inputs):
            return FinalResponse(
                answer="Mock response (no API key configured). Please set OPENAI_API_KEY.",
                sql_used=inputs.get("sql", ""),
                confidence=0.5,
                follow_up_questions=["Set your API key to see real responses."],
                warnings=["Running in demo mode."]
            )
        return mock_response

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior data analyst presenting insights to a business user.

Synthesize the SQL results and analysis into a clear, actionable answer. Include:
1. A direct answer to the user's question
2. Key numbers and trends
3. 2-3 follow-up questions they might ask next
4. Any caveats or warnings about the data

Keep it concise but insightful."""),
        ("human", """User Query: {query}
SQL Executed: {sql}
Results Summary: {results_summary}
Analysis: {analysis}
Chart Generated: {has_chart}

Generate the final response.""")
    ])

    chain = (
        RunnablePassthrough.assign(
            results_summary=lambda x: str(x.get("results", {}))[:1000],
            analysis=lambda x: str(x.get("analysis", {}))[:500],
            has_chart=lambda x: "Yes" if x.get("chart") else "No"
        )
        | prompt
        | llm.with_structured_output(FinalResponse)
    )

    return chain
