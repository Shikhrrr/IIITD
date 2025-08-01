from flask import Flask, request, jsonify
from config import Config
from db import create_database
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
        "message": "WhatsApp Sales Analytics Bot - Test Mode",
        "status": "running",
        "endpoints": {
            "test_query": "/test-query",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/test-query', methods=['POST'])
def test_query():
    """Test endpoint for AI queries without WhatsApp"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Please provide a 'question' in the request body"}), 400
        
        question = data['question']
        logger.info(f"Processing test query: {question}")
        
        # Process the query with AI
        response = ai_processor.process_query(question)
        
        return jsonify({
            "question": question,
            "response": response,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error processing test query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sample-questions')
def sample_questions():
    """Get sample questions"""
    questions = ai_processor.get_sample_questions()
    return jsonify({
        "sample_questions": questions
    })

if __name__ == '__main__':
    # Create database and sample data
    create_database()
    logger.info("Database initialized with sample data")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    ) 