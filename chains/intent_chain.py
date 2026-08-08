"""Intent extraction chain using LCEL and structured outputs."""
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schemas import UserIntent
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE

def format_chat_history(history: list) -> str:
    """Format conversation history for prompt context."""
    if not history:
        return "No previous conversation."
    formatted = []
    for msg in history[-6:]:  # Last 6 messages for context
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role.upper()}: {content}")
    return "\n".join(formatted)

def build_intent_chain():
    """Build the intent extraction LCEL chain.

    Pipeline: input -> format history -> prompt -> LLM with structured output -> UserIntent
    """
    if not OPENAI_API_KEY:
        # Fallback: return a mock chain for demo without API key
        def mock_intent(inputs):
            return UserIntent(
                intent_type="aggregation",
                entities=["products", "revenue"],
                time_range="Q2 2024",
                requires_chart=True,
                ambiguity_flags=[],
                confidence=0.95
            )
        return mock_intent

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert data analyst assistant. Extract the user's analytical intent from their natural language query.

Analyze the query and identify:
1. Intent type: aggregation, comparison, trend, lookup, anomaly, or unknown
2. Entities: tables, columns, metrics, product names, regions mentioned
3. Time range: any temporal filters
4. Whether a chart would be helpful
5. Any ambiguous terms that need clarification

Be precise and concise."""),
        ("human", "Query: {query}\n\nConversation History:\n{formatted_history}")
    ])

    chain = (
        RunnablePassthrough.assign(
            formatted_history=lambda x: format_chat_history(x.get("history", []))
        )
        | prompt
        | llm.with_structured_output(UserIntent)
    )

    return chain
