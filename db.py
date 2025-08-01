import uuid
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite database file
DATABASE_FILE = 'sales.db'

def create_database():
    """Create the SQLite database with schema and sample data"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops (
                id TEXT PRIMARY KEY,
                name TEXT,
                owner_phone TEXT UNIQUE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                shop_id TEXT REFERENCES shops(id),
                name TEXT,
                cost_price REAL,
                selling_price REAL,
                expiry_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id TEXT PRIMARY KEY,
                item_id TEXT REFERENCES items(id),
                quantity_sold INTEGER,
                profit REAL,
                sale_date TEXT DEFAULT CURRENT_DATE
            )
        ''')
        
        # Clear existing data
        cursor.execute('DELETE FROM sales')
        cursor.execute('DELETE FROM items')
        cursor.execute('DELETE FROM shops')
        
        # Add sample data
        populate_sample_data_sqlite(cursor)
        
        conn.commit()
        conn.close()
        
        logger.info("SQLite database created and sample data populated successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False

def populate_sample_data_sqlite(cursor):
    """Populate the SQLite database with sample data"""
    try:
        # Sample shop data
        shops = [
            (str(uuid.uuid4()), "Grocery Store", "+1234567890"),
            (str(uuid.uuid4()), "Convenience Store", "+9876543210"),
            (str(uuid.uuid4()), "Supermarket", "+1122334455")
        ]
        
        # Insert shops
        cursor.executemany('INSERT INTO shops (id, name, owner_phone) VALUES (?, ?, ?)', shops)
        
        # Sample items
        items = []
        item_names = [
            'Milk', 'Bread', 'Eggs', 'Cheese', 'Yogurt', 'Butter', 'Chicken', 'Beef',
            'Fish', 'Rice', 'Pasta', 'Tomatoes', 'Onions', 'Potatoes', 'Apples', 'Bananas'
        ]
        
        # Create items for each shop
        for shop_id, shop_name, _ in shops:
            for item_name in item_names:
                item_id = str(uuid.uuid4())
                cost_price = round(float(f"{(2 + (hash(item_name) % 5)):.2f}"), 2)
                selling_price = round(cost_price * 1.3, 2)  # 30% markup
                
                # Random expiry date (1-60 days from now)
                expiry_days = (hash(item_name) % 60) + 1
                expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
                
                item = (item_id, shop_id, item_name, cost_price, selling_price, expiry_date)
                items.append(item)
                
                # Insert item
                cursor.execute('INSERT INTO items (id, shop_id, name, cost_price, selling_price, expiry_date) VALUES (?, ?, ?, ?, ?, ?)', item)
        
        # Generate sample sales data
        for _ in range(100):
            # Pick a random item
            item = items[hash(str(uuid.uuid4())) % len(items)]
            
            # Random quantity and calculate profit
            quantity = (hash(str(uuid.uuid4())) % 10) + 1
            profit = round((item[4] - item[3]) * quantity, 2)  # selling_price - cost_price
            
            # Random sale date in the last 30 days
            days_ago = (hash(str(uuid.uuid4())) % 30)
            sale_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            sale = (str(uuid.uuid4()), item[0], quantity, profit, sale_date)
            cursor.execute('INSERT INTO sales (id, item_id, quantity_sold, profit, sale_date) VALUES (?, ?, ?, ?, ?)', sale)
        
        logger.info("Sample data populated successfully")
        
    except Exception as e:
        logger.error(f"Error populating sample data: {str(e)}")
        raise e

def get_shop_id_by_phone(phone_number):
    """Get shop ID by phone number"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM shops WHERE owner_phone = ?', (phone_number,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting shop ID: {str(e)}")
        return None

def execute_query(query, params=None, phone_number=None):
    """Execute a SQL query and return results"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get shop_id if phone number is provided (for filtering by shop)
        shop_id = None
        if phone_number:
            shop_id = get_shop_id_by_phone(phone_number)
        
        # Execute the query
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Get results
        results = cursor.fetchall()
        
        conn.close()
        return columns, results
        
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise e

def get_expiring_items(days=3):
    """Get items that will expire within the specified number of days"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Calculate the date threshold
        threshold_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Query items that will expire soon
        cursor.execute('''
            SELECT i.*, s.name as shop_name, s.owner_phone 
            FROM items i 
            JOIN shops s ON i.shop_id = s.id 
            WHERE i.expiry_date <= ? AND i.expiry_date >= ?
        ''', (threshold_date, current_date))
        
        results = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = [description[0] for description in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in results]
        
    except Exception as e:
        logger.error(f"Error getting expiring items: {str(e)}")
        return []

def get_database_schema_info():
    """Get the database schema information for AI prompts"""
    schema_info = """
    CREATE TABLE shops (
        id TEXT PRIMARY KEY,
        name TEXT,
        owner_phone TEXT UNIQUE
    );
    
    CREATE TABLE items (
        id TEXT PRIMARY KEY,
        shop_id TEXT REFERENCES shops(id),
        name TEXT,
        cost_price REAL,
        selling_price REAL,
        expiry_date TEXT
    );
    
    CREATE TABLE sales (
        id TEXT PRIMARY KEY,
        item_id TEXT REFERENCES items(id),
        quantity_sold INTEGER,
        profit REAL,
        sale_date TEXT DEFAULT CURRENT_DATE
    );
    """
    return schema_info

# Legacy functions for compatibility
def create_database_schema():
    """Legacy function - redirects to create_database"""
    return create_database()