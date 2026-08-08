"""Generate a realistic sample ecommerce SQLite database."""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DB_PATH = Path(__file__).parent / "sample_ecommerce.db"
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_ORDERS = 2000

# Seed for reproducibility
random.seed(42)

# Sample data pools
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
               "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
REGIONS = [
    ("North", "USA"), ("South", "USA"), ("East", "USA"), ("West", "USA"),
    ("Ontario", "Canada"), ("Quebec", "Canada"), ("BC", "Canada"),
    ("England", "UK"), ("Scotland", "UK"), ("Wales", "UK"),
    ("Bavaria", "Germany"), ("Berlin", "Germany"),
    ("Maharashtra", "India"), ("Karnataka", "India"), ("Delhi", "India"),
    ("Tokyo", "Japan"), ("Osaka", "Japan"),
    ("Sydney", "Australia"), ("Melbourne", "Australia")
]
PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", "Health"]
PRODUCT_NAMES = {
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Bluetooth Speaker", "USB-C Hub", "Power Bank",
                    "Webcam 4K", "Mechanical Keyboard", "Gaming Mouse", "Monitor 27\"", "SSD 1TB"],
    "Clothing": ["Cotton T-Shirt", "Denim Jeans", "Running Shoes", "Winter Jacket", "Yoga Pants",
                 "Wool Sweater", "Baseball Cap", "Leather Belt", "Socks Pack", "Hoodie"],
    "Home & Garden": ["LED Desk Lamp", "Air Purifier", "Coffee Maker", "Throw Pillow", "Succulent Pot",
                      "Kitchen Scale", "Vacuum Cleaner", "Wall Shelf", "Bedding Set", "Garden Hose"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Tennis Racket", "Cycling Helmet", "Resistance Bands",
               "Foam Roller", "Jump Rope", "Swimming Goggles", "Hiking Backpack", "Protein Shaker"],
    "Books": ["Python Mastery", "Data Science Handbook", "Design Patterns", "Clean Code", "AI Revolution",
              "Startup Guide", "Finance 101", "History Atlas", "Sci-Fi Anthology", "Cookbook"],
    "Toys": ["Building Blocks", "RC Car", "Board Game", "Puzzle 1000pc", "Action Figure",
             "Doll House", "Science Kit", "Plush Bear", "Art Set", "Drone Mini"],
    "Health": ["Vitamin D3", "Probiotics", "Face Serum", "Sunscreen SPF50", "Hand Sanitizer",
               "First Aid Kit", "Massage Gun", "Digital Thermometer", "Sleep Mask", "Essential Oils"]
}
STATUSES = ["completed", "completed", "completed", "completed", "completed", 
            "shipped", "shipped", "processing", "cancelled", "returned"]

def create_database():
    """Create and populate the sample ecommerce database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS regions;
    """)

    # Create regions table
    cursor.execute("""
        CREATE TABLE regions (
            region_id INTEGER PRIMARY KEY,
            region_name TEXT NOT NULL,
            country TEXT NOT NULL
        )
    """)

    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            region_id INTEGER,
            signup_date DATE,
            FOREIGN KEY (region_id) REFERENCES regions(region_id)
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL,
            cost_price REAL NOT NULL
        )
    """)

    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    # Insert regions
    region_data = [(i+1, name, country) for i, (name, country) in enumerate(REGIONS)]
    cursor.executemany("INSERT INTO regions VALUES (?, ?, ?)", region_data)

    # Insert customers
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        name = f"{fname} {lname}"
        email = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}@example.com"
        region_id = random.randint(1, len(REGIONS))
        signup_date = (datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900))).strftime("%Y-%m-%d")
        customers.append((i, name, email, region_id, signup_date))
    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)

    # Insert products
    products = []
    pid = 1
    for category in PRODUCT_CATEGORIES:
        for pname in PRODUCT_NAMES[category]:
            unit_price = round(random.uniform(9.99, 499.99), 2)
            cost_price = round(unit_price * random.uniform(0.4, 0.7), 2)
            products.append((pid, pname, category, unit_price, cost_price))
            pid += 1
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?)", products)

    # Insert orders
    orders = []
    start_date = datetime(2023, 1, 1)
    for i in range(1, NUM_ORDERS + 1):
        customer_id = random.randint(1, NUM_CUSTOMERS)
        product_id = random.randint(1, len(products))
        quantity = random.randint(1, 5)
        # Get product price
        cursor.execute("SELECT unit_price FROM products WHERE product_id = ?", (product_id,))
        unit_price = cursor.fetchone()[0]
        order_date = (start_date + timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d")
        status = random.choice(STATUSES)
        orders.append((i, customer_id, product_id, quantity, unit_price, order_date, status))
    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()
    print(f"✅ Sample database created at: {DB_PATH}")
    print(f"   - {len(REGIONS)} regions")
    print(f"   - {NUM_CUSTOMERS} customers")
    print(f"   - {len(products)} products")
    print(f"   - {NUM_ORDERS} orders")

if __name__ == "__main__":
    create_database()
