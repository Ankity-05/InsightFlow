"""InsightFlow — Conversational Multi-Agent Data Intelligence Platform

Streamlit entry point that orchestrates the full pipeline:
1. Intent Extraction
2. SQL Generation
3. Validation & Approval
4. Agentic Execution
5. Structured Response
"""
import os
import sys
import time
import json
import sqlite3
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# LangChain / LangGraph imports
from langchain_core.messages import HumanMessage, AIMessage

# Project modules
from config import DB_PATH, OPENAI_API_KEY, ROLE_PERMISSIONS
from schemas import UserIntent, SQLQuery, SQLValidation, FinalResponse
from chains import build_intent_chain, build_sql_chain, build_validation_chain, build_response_chain
from tools import execute_sql_query, get_table_schema, get_table_names, validate_sql
from tools import calculate_statistics, anomaly_detector, generate_chart
from controllers import ManualToolController, ApprovalGate, ErrorHandler
from agents import build_sql_agent, build_analysis_agent, build_conversational_agent

# Page config
st.set_page_config(
    page_title="InsightFlow",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; }
    .sub-header { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    .stChatMessage { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .metric-card { background: #f0f2f6; padding: 1rem; border-radius: 10px; }
    .sql-box { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem; }
    .warning-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 0.75rem; border-radius: 4px; }
    .success-box { background: #d4edda; border-left: 4px solid #28a745; padding: 0.75rem; border-radius: 4px; }
    .error-box { background: #f8d7da; border-left: 4px solid #dc3545; padding: 0.75rem; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def init_session_state():
    defaults = {
        "messages": [],
        "chat_history": [],
        "user_role": "analyst",
        "api_key_set": bool(OPENAI_API_KEY),
        "last_sql": None,
        "last_results": None,
        "last_chart": None,
        "execution_log": [],
        "pending_approval": None,
        "show_sql": True,
        "show_schema": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🚀 InsightFlow")
    st.markdown("*Conversational Data Intelligence*")
    st.divider()

    # API Key input
    if not st.session_state.api_key_set:
        api_key_input = st.text_input("OpenAI API Key", type="password", 
                                       placeholder="sk-...", key="api_key_input")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.session_state.api_key_set = True
            st.rerun()
    else:
        st.success("✅ API Key configured")
        if st.button("Reset API Key"):
            st.session_state.api_key_set = False
            os.environ["OPENAI_API_KEY"] = ""
            st.rerun()

    st.divider()

    # Role selector
    st.session_state.user_role = st.selectbox(
        "Your Role",
        options=["viewer", "analyst", "admin"],
        index=["viewer", "analyst", "admin"].index(st.session_state.user_role)
    )

    st.info(f"Permissions: {', '.join(ROLE_PERMISSIONS.get(st.session_state.user_role, []))}")

    st.divider()

    # Settings
    st.session_state.show_sql = st.toggle("Show generated SQL", value=st.session_state.show_sql)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.last_sql = None
        st.session_state.last_results = None
        st.session_state.last_chart = None
        st.rerun()

    st.divider()

    # Schema explorer
    with st.expander("📋 Database Schema"):
        try:
            tables = get_table_names.invoke({})
            for table in tables:
                schema = get_table_schema.invoke({"table_name": table})
                st.markdown(f"**{table}**")
                cols = [f"{c['name']} ({c['type']})" for c in schema.get("columns", [])]
                st.markdown(", ".join(cols))
        except Exception as e:
            st.error(f"Could not load schema: {e}")

    st.divider()
    st.caption("Built with LangChain + LangGraph + Streamlit")

# ==================== MAIN UI ====================
st.markdown('<div class="main-header">🚀 InsightFlow</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about your data in plain English. Get SQL, charts, and insights.</div>', unsafe_allow_html=True)

# Approval gate UI
if st.session_state.pending_approval:
    pending = st.session_state.pending_approval
    with st.container():
        st.warning("⚠️ **Approval Required**")
        st.markdown(f"**Reason:** {pending['reason']}")
        st.markdown(f"**Query:** `{pending['query']}`")
        col_a, col_r = st.columns(2)
        with col_a:
            if st.button("✅ Approve", key="approve_btn"):
                st.session_state.pending_approval = None
                st.session_state.messages.append({"role": "assistant", "content": "✅ Operation approved by user."})
                st.rerun()
        with col_r:
            if st.button("❌ Reject", key="reject_btn"):
                st.session_state.pending_approval = None
                st.session_state.messages.append({"role": "assistant", "content": "❌ Operation rejected by user."})
                st.rerun()
    st.divider()

# Chat display
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and isinstance(msg.get("content"), dict):
            # Structured response rendering
            render_structured_response(msg["content"])
        else:
            st.markdown(msg["content"])

def render_structured_response(response: dict):
    """Render a FinalResponse dict in the chat UI."""
    # Answer
    st.markdown(f"### {response.get('answer', 'No answer provided.')}")

    # SQL
    if st.session_state.show_sql and response.get('sql_used'):
        with st.expander("🔍 Generated SQL"):
            st.code(response['sql_used'], language="sql")

    # Chart
    if response.get('chart_data'):
        try:
            fig = go.Figure(response['chart_data'])
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not render chart: {e}")

    # Data table
    if response.get('table_data'):
        st.dataframe(pd.DataFrame(response['table_data']), use_container_width=True)

    # Metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Confidence", f"{response.get('confidence', 0)*100:.0f}%")
    with cols[1]:
        st.metric("Execution Time", f"{response.get('execution_time_ms', 0)}ms")
    with cols[2]:
        st.metric("Rows Returned", response.get('row_count', 0))

    # Follow-ups
    if response.get('follow_up_questions'):
        st.markdown("**💡 Follow-up Questions:**")
        for q in response['follow_up_questions']:
            st.markdown(f"- {q}")

    # Warnings
    if response.get('warnings'):
        for w in response['warnings']:
            st.markdown(f'<div class="warning-box">⚠️ {w}</div>', unsafe_allow_html=True)

# ==================== PIPELINE ====================
def run_pipeline(user_query: str) -> dict:
    """Execute the full InsightFlow pipeline.

    Returns a dict compatible with FinalResponse for UI rendering.
    """
    start_time = time.time()

    # Initialize controllers
    controller = ManualToolController(user_role=st.session_state.user_role)
    approval_gate = ApprovalGate()

    try:
        # STEP 1: Intent Extraction
        with st.status("🔍 Extracting intent...", expanded=False) as status:
            intent_chain = build_intent_chain()
            intent = intent_chain.invoke({
                "query": user_query,
                "history": st.session_state.chat_history
            })
            if isinstance(intent, dict):
                intent = UserIntent(**intent)
            status.update(label=f"Intent: {intent.intent_type} | Entities: {', '.join(intent.entities)}", state="complete")

        # STEP 2: SQL Generation
        with st.status("📝 Generating SQL...", expanded=False) as status:
            sql_chain = build_sql_chain()
            schema_hint = "Tables: customers, products, orders, regions"
            sql_result = sql_chain.invoke({
                "intent": intent.model_dump(),
                "query": user_query,
                "schema": schema_hint
            })
            if isinstance(sql_result, dict):
                sql_result = SQLQuery(**sql_result)
            status.update(label=f"SQL ready: {sql_result.query[:60]}...", state="complete")

        # STEP 3: Validation
        with st.status("🛡️ Validating query...", expanded=False) as status:
            validation = validate_sql.invoke({
                "query": sql_result.query,
                "user_role": st.session_state.user_role
            })
            if isinstance(validation, dict):
                validation = SQLValidation(**validation)
            status.update(label=f"Validation: {'✅ Pass' if validation.is_valid else '⚠️ Issues'}", state="complete")

        # STEP 4: Approval Gate
        approval = approval_gate.check_approval_needed(
            validation=validation.model_dump(),
            query=sql_result.query,
            user_role=st.session_state.user_role
        )

        if not approval["approved"] and approval["requires_interaction"]:
            st.session_state.pending_approval = {
                "query": sql_result.query,
                "reason": approval["reason"],
                "approval_id": approval.get("approval_id")
            }
            return {
                "answer": f"⏸️ This query requires approval: {approval['reason']}",
                "sql_used": sql_result.query,
                "confidence": 0.0,
                "follow_up_questions": [],
                "warnings": ["Awaiting user approval"],
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        if not approval["approved"]:
            return {
                "answer": f"❌ Query blocked: {approval['reason']}",
                "sql_used": sql_result.query,
                "confidence": 0.0,
                "follow_up_questions": [],
                "warnings": validation.errors + validation.warnings,
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        # STEP 5: Execute SQL
        with st.status("⚡ Executing query...", expanded=False) as status:
            exec_result = execute_sql_query.invoke({
                "query": sql_result.query,
                "max_rows": 1000
            })
            status.update(label=f"Returned {exec_result.get('row_count', 0)} rows", state="complete")

        if not exec_result.get("success"):
            return {
                "answer": f"❌ Execution failed: {exec_result.get('error', 'Unknown error')}",
                "sql_used": sql_result.query,
                "confidence": 0.0,
                "follow_up_questions": ["Try a simpler query", "Check available tables"],
                "warnings": [],
                "execution_time_ms": int((time.time() - start_time) * 1000)
            }

        rows = exec_result.get("rows", [])
        columns = exec_result.get("columns", [])

        # STEP 6: Analysis & Visualization
        chart_data = None
        analysis_summary = {}

        if intent.requires_chart and rows:
            with st.status("📊 Generating chart...", expanded=False) as status:
                # Auto-detect chart config
                chart_type = "bar"
                x_col = columns[0] if columns else None
                y_col = columns[1] if len(columns) > 1 else None

                if intent.intent_type == "trend":
                    chart_type = "line"
                elif intent.intent_type == "comparison" and len(rows) <= 6:
                    chart_type = "pie"

                if x_col and y_col:
                    chart_result = generate_chart.invoke({
                        "data_json": rows,
                        "chart_type": chart_type,
                        "x_column": x_col,
                        "y_column": y_col,
                        "title": user_query[:50]
                    })
                    if chart_result.get("success"):
                        chart_data = chart_result.get("chart_json")
                status.update(label="Chart generated" if chart_data else "Chart skipped", state="complete")

        # STEP 7: Response Synthesis
        with st.status("🧠 Synthesizing insights...", expanded=False) as status:
            response_chain = build_response_chain()

            # Build results summary
            results_summary = {
                "columns": columns,
                "row_count": len(rows),
                "sample": rows[:3] if rows else []
            }

            final_response = response_chain.invoke({
                "query": user_query,
                "sql": sql_result.query,
                "results": results_summary,
                "analysis": analysis_summary,
                "chart": bool(chart_data)
            })

            if isinstance(final_response, dict):
                final_response = FinalResponse(**final_response)
            status.update(label="Response ready", state="complete")

        # Build renderable response
        render_response = {
            "answer": final_response.answer,
            "sql_used": sql_result.query,
            "chart_data": chart_data,
            "table_data": rows,
            "confidence": final_response.confidence,
            "follow_up_questions": final_response.follow_up_questions,
            "warnings": final_response.warnings + validation.warnings,
            "execution_time_ms": int((time.time() - start_time) * 1000),
            "row_count": len(rows)
        }

        # Store for context
        st.session_state.last_sql = sql_result.query
        st.session_state.last_results = rows
        st.session_state.last_chart = chart_data

        return render_response

    except Exception as e:
        error = ErrorHandler.handle(e, context={"query": user_query})
        return {
            "answer": f"❌ {error['user_message']}\n\n*{error['hint']}*",
            "sql_used": st.session_state.last_sql or "N/A",
            "confidence": 0.0,
            "follow_up_questions": ["Try rephrasing your question"],
            "warnings": [error['technical_detail']],
            "execution_time_ms": int((time.time() - start_time) * 1000)
        }

# ==================== CHAT INPUT ====================
user_input = st.chat_input("Ask about your data... (e.g., 'Top 5 products by revenue in Q2')")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run pipeline
    with st.chat_message("assistant"):
        response = run_pipeline(user_input)
        render_structured_response(response)

    # Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_history.append({"role": "assistant", "content": response.get("answer", "")})

    # Rerun to update UI cleanly
    st.rerun()

# Footer
st.divider()
st.caption("InsightFlow v1.0 | LangChain + LangGraph + Streamlit | [GitHub](https://github.com)")
