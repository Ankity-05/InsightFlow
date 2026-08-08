"""Central configuration for InsightFlow."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sample_ecommerce.db"
SAMPLE_QUERIES_PATH = DATA_DIR / "sample_queries.json"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM Settings
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

# Security
MAX_ROWS_DEFAULT = 1_000
MAX_ROWS_HARD_LIMIT = 10_000
FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
PII_COLUMNS = ["email", "phone", "address", "credit_card", "ssn"]

# Roles & Permissions
ROLE_PERMISSIONS = {
    "admin": ["execute_sql_query", "generate_chart", "calculate_statistics", 
              "anomaly_detector", "delete_records"],
    "analyst": ["execute_sql_query", "generate_chart", "calculate_statistics", "anomaly_detector"],
    "viewer": ["execute_sql_query", "generate_chart"]
}

# Few-shot examples for SQL generation
FEW_SHOT_EXAMPLES = [
    {
        "input": "Top 5 products by revenue in Q2 2024",
        "sql": """SELECT p.product_name, SUM(o.quantity * o.unit_price) as revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.order_date >= '2024-04-01' AND o.order_date < '2024-07-01'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 5;""",
        "explanation": "Joins orders and products, filters Q2 2024, aggregates revenue."
    },
    {
        "input": "Monthly sales trend for 2024",
        "sql": """SELECT strftime('%Y-%m', order_date) as month, SUM(quantity * unit_price) as revenue
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY month
ORDER BY month;""",
        "explanation": "Groups by month using SQLite strftime, sums revenue."
    },
    {
        "input": "Customers who spent more than $5000",
        "sql": """SELECT c.customer_name, SUM(o.quantity * o.unit_price) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
HAVING total_spent > 5000
ORDER BY total_spent DESC;""",
        "explanation": "Uses HAVING clause to filter aggregated spend."
    }
]
