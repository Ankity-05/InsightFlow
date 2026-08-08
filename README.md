# 🚀 InsightFlow — Conversational Multi-Agent Data Intelligence Platform

A production-grade Agentic AI system that lets business users talk to their databases using natural language, with full human-in-the-loop control, structured reasoning, and multi-step agentic workflows.

---

## 📋 Overview

**InsightFlow** bridges the gap between non-technical users and complex databases by combining:

- **Tool Calling & Chaining** — Custom tools for SQL execution, data visualization, and API calls
- **LCEL** — Composing the entire pipeline using `RunnableSequence`, `RunnableParallel`, and `.pipe()`
- **Structured Outputs** — Pydantic schemas to parse user intent, validate SQL, and format responses
- **Manual Tool Calling** — Human-in-the-loop approval for destructive SQL operations with custom business logic
- **NLI for Data Systems** — Converting natural language to SQL, analyzing results, generating insights
- **Built-in Agents** — A ReAct agent for reasoning + a LangGraph agent for multi-step data exploration

---

## 🏗️ Architecture

```
User Query → Intent Extraction → SQL Generation → Validation Gate → 
Agentic Execution → Analysis & Viz → Structured Response → Streamlit UI
```

| Step | Component | Technology |
|------|-----------|------------|
| 1 | Intent Extraction | LCEL + Pydantic Structured Output |
| 2 | SQL Generation | Few-shot Prompting + LLM |
| 3 | Validation | Parallel Checks (Syntax, Injection, Permissions) |
| 4 | Approval Gate | Human-in-the-loop for sensitive ops |
| 5 | Execution | LangGraph ReAct Agent |
| 6 | Analysis | Statistical tools + Anomaly detection |
| 7 | Visualization | Plotly charts auto-generated |
| 8 | Response | Structured JSON → Streamlit |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | LangChain + LangGraph |
| LLM | OpenAI GPT-4o / GPT-4o-mini |
| Data | SQLite + Pandas |
| Schemas | Pydantic v2 |
| Agents | `create_react_agent` (LangGraph) + `initialize_agent` (core) |
| Visualization | Plotly |
| UI | Streamlit |
| Memory | LangChain ConversationBufferMemory |

---

## 📁 Project Structure

```
insightflow/
├── main.py                          # Streamlit entry point
├── config.py                        # API keys, DB connections, constants
│
├── tools/                           # Custom tools
│   ├── sql_tools.py                 # SQL execution, schema discovery
│   ├── analysis_tools.py            # Statistics, anomaly detection
│   ├── viz_tools.py                 # Plotly chart generation
│   └── security_tools.py            # SQL validation, permissions
│
├── chains/                          # LCEL pipelines
│   ├── intent_chain.py              # Intent extraction
│   ├── sql_generation_chain.py      # SQL generation with few-shot
│   ├── validation_chain.py          # Parallel validation
│   └── response_chain.py            # Final response synthesis
│
├── agents/                          # Agent definitions
│   ├── sql_agent.py                 # LangGraph ReAct SQL agent
│   ├── analysis_agent.py            # LangGraph analysis agent
│   └── conversational_agent.py      # Conversational agent with memory
│
├── schemas/                         # Pydantic models
│   ├── intent_schema.py
│   ├── sql_schema.py
│   ├── analysis_schema.py
│   └── response_schema.py
│
├── controllers/                     # Security & control
│   ├── manual_tool_controller.py    # Conditional execution gates
│   ├── approval_gate.py             # Human-in-the-loop logic
│   └── error_handler.py             # Categorized error handling
│
├── data/
│   ├── create_sample_db.py          # DB generator script
│   ├── sample_ecommerce.db          # SQLite database (auto-generated)
│   └── sample_queries.json          # Few-shot examples
│
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Generate Sample Database

```bash
cd data
python create_sample_db.py
cd ..
```

### 4. Run the App

```bash
streamlit run main.py
```

---

## 🎯 Sample Queries

| User Query | System Behavior |
|------------|-----------------|
| *"Top 5 products by revenue in Q2"* | Generates SQL → validates → executes → bar chart → insight summary |
| *"How are sales this year?"* | Detects ambiguity → asks for clarification |
| *"Why did sales drop in March?"* | Root-cause analysis with regional breakdown |
| *"Compare that to last year"* | Conversational memory maintains context |
| *"Delete all test orders"* | Manual gate blocks: "Destructive ops require admin MFA" |

---

## 🔑 Key Features

### 1. Tool Creation & Calling
- `@tool` decorator for simple functions
- `StructuredTool.from_function()` for complex inputs
- Manual tool calling with role-based permissions

### 2. LCEL Composition
- `RunnableSequence` for linear pipelines
- `RunnableParallel` for parallel validation
- `.with_retry()` for resilient SQL generation

### 3. Structured Outputs
- `UserIntent` — parsed query understanding
- `SQLQuery` — generated SQL with metadata
- `SQLValidation` — comprehensive safety checks
- `FinalResponse` — guaranteed UI contract

### 4. Security & Control
- Forbidden keyword detection (DROP, DELETE, etc.)
- SQL injection pattern scanning
- PII column detection and warnings
- Row limit enforcement (soft + hard limits)
- Role-based tool permissions

### 5. Agents
- **SQL Agent**: LangGraph ReAct for schema-aware querying
- **Analysis Agent**: Statistical analysis + anomaly detection
- **Conversational Agent**: Memory-enabled follow-up handling

---

## 🛡️ Security Features

| Feature | Implementation |
|---------|---------------|
| Read-only mode | `PRAGMA query_only = ON` |
| Destructive op blocking | Keyword blacklist + approval gate |
| SQL injection detection | Regex pattern matching |
| PII warnings | Column name scanning |
| Role-based access | `ROLE_PERMISSIONS` config |
| Row limits | Soft default 1,000 / Hard limit 10,000 |
| Audit logging | `ManualToolController.execution_log` |

---

## 📊 Database Schema

The sample database includes:

- **regions** — 19 regions across 8 countries
- **customers** — 200 customers with signup dates
- **products** — 70 products across 7 categories
- **orders** — 2,000 orders with quantities, prices, dates, and statuses

---

## 🎓 Why This Project Stands Out

| Aspect | Coverage |
|--------|----------|
| **Complete LangChain mastery** | Tools, LCEL, Agents, Structured Output all integrated |
| **Production-ready patterns** | Manual tool calling, validation gates, error handling |
| **Real-world problem** | NLIs for data are high-demand (BI tools, analytics platforms) |
| **Portfolio-worthy** | Complex enough to demonstrate system design, simple enough to build in 2-3 weeks |
| **Extensible** | Swap SQLite for Snowflake/BigQuery, add Slack/Teams bot, deploy with LangServe |

---

## 📄 License

MIT License — free for personal and commercial use.
