import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    """Create the sales database with sample data"""
    conn = sqlite3.connect('sales.db')
    cursor = conn.cursor()
    
    # Create sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity_sold INTEGER NOT NULL,
            profit REAL NOT NULL,
            expiry_date DATE NOT NULL,
            sale_date DATE NOT NULL
        )
    ''')
    
    # Check if table is empty, if so add sample data
    cursor.execute('SELECT COUNT(*) FROM sales')
    if cursor.fetchone()[0] == 0:
        # Sample data
        items = [
            'Milk', 'Bread', 'Eggs', 'Cheese', 'Yogurt', 'Butter', 'Chicken', 'Beef',
            'Fish', 'Rice', 'Pasta', 'Tomatoes', 'Onions', 'Potatoes', 'Apples', 'Bananas'
        ]
        
        # Generate sample sales data for the last 30 days
        for _ in range(100):
            item = random.choice(items)
            quantity = random.randint(1, 50)
            profit = round(random.uniform(0.5, 10.0), 2)
            
            # Random sale date in the last 30 days
            sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Random expiry date (1-30 days from sale date)
            expiry_date = sale_date + timedelta(days=random.randint(1, 30))
            
            cursor.execute('''
                INSERT INTO sales (item_name, quantity_sold, profit, expiry_date, sale_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (item, quantity, profit, expiry_date.strftime('%Y-%m-%d'), sale_date.strftime('%Y-%m-%d')))
    
    conn.commit()
    conn.close()

def get_database_connection():
    """Get a connection to the SQLite database"""
    return sqlite3.connect('sales.db')

def execute_query(query):
    """Execute a SQL query and return results"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        return columns, results
    except Exception as e:
        conn.close()
        raise e 