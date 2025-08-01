from flask import Flask, request, jsonify
from config import Config
from db import create_database_schema
from ai import AIQueryProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize AI processor
ai_processor = AIQueryProcessor()

@app.route('/')
def home():
    """Home page with basic information"""
    return jsonify({
        "message": "Sales Analytics Bot API",
        "status": "running",
        "endpoints": {
            "query": "/query",
            "health": "/health",
            "sample_questions": "/sample-questions"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/query', methods=['POST'])
def process_query():
    """Process a natural language query"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        query = data['query']
        language = data.get('language', 'en')
        phone_number = data.get('phone_number', None)
        
        logger.info(f"Processing query: {query} (language: {language})")
        
        # Process the query with AI
        response = ai_processor.process_query(query, language, phone_number)
        
        return jsonify({
            "success": True,
            "query": query,
            "language": language,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sample-questions')
def get_sample_questions():
    """Get sample questions"""
    try:
        language = request.args.get('language', 'en')
        questions = ai_processor.get_sample_questions(language)
        
        return jsonify({
            "success": True,
            "language": language,
            "questions": questions
        })
        
    except Exception as e:
        logger.error(f"Error getting sample questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create database and sample data
    create_database_schema()
    logger.info("Database schema initialized")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=Config.DEBUG
    ) 