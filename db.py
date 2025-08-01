import uuid
import logging
import json
from datetime import datetime, timedelta
from supabase import create_client
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def create_database_schema():
    """Create the database schema in Supabase"""
    try:
        # Create shops table
        supabase.table('shops').delete().execute()
        supabase.table('items').delete().execute()
        supabase.table('sales').delete().execute()
        
        logger.info("Creating database schema...")
        
        # Note: In Supabase, we don't need to create tables via SQL as they should be
        # created through the Supabase dashboard or migrations
        # This function will just populate sample data
        
        # Add sample data
        populate_sample_data()
        
        logger.info("Database schema created and sample data populated successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database schema: {str(e)}")
        return False

def populate_sample_data():
    """Populate the database with sample data"""
    try:
        # Sample shop data
        shops = [
            {"id": str(uuid.uuid4()), "name": "Grocery Store", "owner_phone": "+1234567890"},
            {"id": str(uuid.uuid4()), "name": "Convenience Store", "owner_phone": "+9876543210"},
            {"id": str(uuid.uuid4()), "name": "Supermarket", "owner_phone": "+1122334455"}
        ]
        
        # Insert shops
        for shop in shops:
            supabase.table('shops').insert(shop).execute()
        
        # Sample items
        items = []
        item_names = [
            'Milk', 'Bread', 'Eggs', 'Cheese', 'Yogurt', 'Butter', 'Chicken', 'Beef',
            'Fish', 'Rice', 'Pasta', 'Tomatoes', 'Onions', 'Potatoes', 'Apples', 'Bananas'
        ]
        
        # Create items for each shop
        for shop in shops:
            for item_name in item_names:
                item_id = str(uuid.uuid4())
                cost_price = round(float(f"{(2 + (hash(item_name) % 5)):.2f}"), 2)
                selling_price = round(cost_price * 1.3, 2)  # 30% markup
                
                # Random expiry date (1-60 days from now)
                expiry_days = (hash(item_name) % 60) + 1
                expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')
                
                item = {
                    "id": item_id,
                    "shop_id": shop["id"],
                    "name": item_name,
                    "cost_price": cost_price,
                    "selling_price": selling_price,
                    "expiry_date": expiry_date
                }
                
                items.append(item)
                
                # Insert item
                supabase.table('items').insert(item).execute()
        
        # Generate sample sales data
        for _ in range(100):
            # Pick a random item
            item = items[hash(str(uuid.uuid4())) % len(items)]
            
            # Random quantity and calculate profit
            quantity = (hash(str(uuid.uuid4())) % 10) + 1
            profit = round((item["selling_price"] - item["cost_price"]) * quantity, 2)
            
            # Random sale date in the last 30 days
            days_ago = (hash(str(uuid.uuid4())) % 30)
            sale_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            sale = {
                "id": str(uuid.uuid4()),
                "item_id": item["id"],
                "quantity_sold": quantity,
                "profit": profit,
                "sale_date": sale_date
            }
            
            # Insert sale
            supabase.table('sales').insert(sale).execute()
        
        logger.info(f"Sample data populated: {len(shops)} shops, {len(items)} items, 100 sales records")
    except Exception as e:
        logger.error(f"Error populating sample data: {str(e)}")
        raise e

def get_shop_id_by_phone(phone_number):
    """Get shop ID based on owner's phone number"""
    try:
        response = supabase.table('shops').select('id').eq('owner_phone', phone_number).execute()
        data = response.data
        
        if data and len(data) > 0:
            return data[0]['id']
        return None
    except Exception as e:
        logger.error(f"Error getting shop ID by phone: {str(e)}")
        return None

def execute_query(query, params=None, phone_number=None):
    """Execute a SQL query against Supabase
    
    This is a wrapper function that translates SQL queries to Supabase API calls
    """
    try:
        # Parse the SQL query to determine the operation and table
        query = query.strip()
        
        # Get shop_id if phone number is provided (for filtering by shop)
        shop_id = None
        if phone_number:
            shop_id = get_shop_id_by_phone(phone_number)
        
        # Handle SELECT queries
        if query.upper().startswith('SELECT'):
            # Extract table name from FROM clause
            from_clause = query.upper().split('FROM')[1].strip().split()[0]
            table_name = from_clause.strip().lower()
            
            # Start building the Supabase query
            supabase_query = supabase.table(table_name).select('*')
            
            # Apply shop_id filter if available and relevant
            if shop_id:
                if table_name == 'shops':
                    supabase_query = supabase_query.eq('id', shop_id)
                elif table_name == 'items':
                    supabase_query = supabase_query.eq('shop_id', shop_id)
                elif table_name == 'sales':
                    # For sales, we need to join with items to filter by shop_id
                    # This is a simplification - in real implementation, you'd need more complex logic
                    # to handle JOINs properly
                    sales_response = supabase_query.execute()
                    sales_data = sales_response.data
                    
                    # Get all items for this shop
                    items_response = supabase.table('items').select('id').eq('shop_id', shop_id).execute()
                    item_ids = [item['id'] for item in items_response.data]
                    
                    # Filter sales by item_ids
                    filtered_sales = [sale for sale in sales_data if sale['item_id'] in item_ids]
                    
                    # Return the filtered results
                    columns = list(filtered_sales[0].keys()) if filtered_sales else []
                    return columns, filtered_sales
            
            # Execute the query
            response = supabase_query.execute()
            data = response.data
            
            # Extract column names and results
            columns = list(data[0].keys()) if data else []
            return columns, data
        
        # For other query types (not fully implemented in this example)
        # In a real implementation, you would need to handle INSERT, UPDATE, DELETE, etc.
        else:
            raise Exception("Only SELECT queries are supported through this interface")
            
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise e

def get_expiring_items(days=3):
    """Get items that will expire within the specified number of days"""
    try:
        # Calculate the date threshold
        threshold_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Query items that will expire soon
        response = supabase.table('items').select('*,shops(name,owner_phone)')\
            .lte('expiry_date', threshold_date)\
            .gte('expiry_date', datetime.now().strftime('%Y-%m-%d'))\
            .execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error getting expiring items: {str(e)}")
        return []

def get_database_schema_info():
    """Get the database schema information for AI prompts"""
    schema_info = """
    CREATE TABLE shops (
        id UUID PRIMARY KEY,
        name TEXT,
        owner_phone TEXT UNIQUE
    );
    
    CREATE TABLE items (
        id UUID PRIMARY KEY,
        shop_id UUID REFERENCES shops(id),
        name TEXT,
        cost_price NUMERIC,
        selling_price NUMERIC,
        expiry_date DATE
    );
    
    CREATE TABLE sales (
        id UUID PRIMARY KEY,
        item_id UUID REFERENCES items(id),
        quantity_sold INTEGER,
        profit NUMERIC,
        sale_date DATE DEFAULT CURRENT_DATE
    );
    """
    return schema_info