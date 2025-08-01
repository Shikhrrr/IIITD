from flask import Flask, request, jsonify
from config import Config
from db import create_database, execute_query
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    """Home page with basic information"""
    return jsonify({
        "message": "Sales Analytics Bot - Simple Test Mode",
        "status": "running",
        "endpoints": {
            "test_query": "/test-query",
            "health": "/health",
            "sample_data": "/sample-data"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/sample-data')
def sample_data():
    """Get sample data from database"""
    try:
        query = "SELECT * FROM sales LIMIT 5"
        columns, results = execute_query(query)
        
        return jsonify({
            "columns": columns,
            "data": results,
            "success": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-query', methods=['POST'])
def test_query():
    """Test endpoint for direct SQL queries"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Please provide a 'query' in the request body"}), 400
        
        sql_query = data['query']
        logger.info(f"Executing SQL query: {sql_query}")
        
        # Execute the query
        columns, results = execute_query(sql_query)
        
        return jsonify({
            "query": sql_query,
            "columns": columns,
            "results": results,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def stats():
    """Get basic statistics"""
    try:
        # Total sales
        total_query = "SELECT COUNT(*) as total_sales FROM sales"
        _, total_results = execute_query(total_query)
        
        # Total profit
        profit_query = "SELECT SUM(profit) as total_profit FROM sales"
        _, profit_results = execute_query(profit_query)
        
        # Top selling items
        top_items_query = """
        SELECT item_name, SUM(quantity_sold) as total_quantity 
        FROM sales 
        GROUP BY item_name 
        ORDER BY total_quantity DESC 
        LIMIT 5
        """
        _, top_items_results = execute_query(top_items_query)
        
        return jsonify({
            "total_sales": total_results[0][0] if total_results else 0,
            "total_profit": round(profit_results[0][0], 2) if profit_results and profit_results[0][0] else 0,
            "top_selling_items": top_items_results,
            "success": True
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create database and sample data
    create_database()
    logger.info("Database initialized with sample data")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=Config.DEBUG
    ) 