"""SQL generation chain using LCEL with few-shot examples."""
from langchain_core.runnables import RunnablePassthrough, RunnableSequence
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from schemas import SQLQuery
from config import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE, FEW_SHOT_EXAMPLES

def build_sql_chain():
    """Build the SQL generation LCEL chain.

    Pipeline: intent + schema -> few-shot prompt -> LLM -> SQLQuery structured output
    """
    if not OPENAI_API_KEY:
        def mock_sql(inputs):
            return SQLQuery(
                query="SELECT * FROM orders LIMIT 10;",
                explanation="Mock SQL generation (no API key configured).",
                estimated_rows=10,
                tables_used=["orders"]
            )
        return mock_sql

    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        temperature=TEMPERATURE,
        api_key=OPENAI_API_KEY
    )

    # Few-shot examples
    examples = FEW_SHOT_EXAMPLES
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "SQL: {sql}\nExplanation: {explanation}")
    ])
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples
    )

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert SQL analyst. Generate a SQLite query based on the user's intent and database schema.

Database Schema:
- customers(customer_id, customer_name, email, region, signup_date)
- products(product_id, product_name, category, unit_price, cost_price)
- orders(order_id, customer_id, product_id, quantity, unit_price, order_date, status)
- regions(region_id, region_name, country)

Rules:
- Only generate SELECT statements
- Use proper JOINs when referencing multiple tables
- Use strftime for date formatting in SQLite
- Add appropriate LIMIT clauses
- Alias aggregated columns clearly

Respond with a JSON object containing: query, explanation, estimated_rows, tables_used."""),
        few_shot_prompt,
        ("human", "User Intent: {intent}\nOriginal Query: {query}\nTable Schema: {schema}")
    ])

    chain = (
        RunnablePassthrough.assign(
            schema=lambda x: x.get("schema", "No schema provided")
        )
        | final_prompt
        | llm.with_structured_output(SQLQuery)
    )

    return chain
