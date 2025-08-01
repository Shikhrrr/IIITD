from flask import Flask, request, jsonify
from config import Config
from db import create_database, execute_query
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# In-memory storage for user language preferences
user_languages = {}

# Language-specific messages
MESSAGES = {
    'en': {
        'welcome': """🤖 *Sales Analytics Bot*

Choose your preferred language / अपनी पसंदीदा भाषा चुनें:

1️⃣ *English* - Continue in English
2️⃣ *हिंदी* - हिंदी में जारी रखें

Reply with 1 or 2 to select language.""",
        'help': """🤖 *Sales Analytics Bot*

Ask me questions about your sales data! Here are some examples:

• "Which item sold the most last week?"
• "What is the total profit for this month?"
• "Which items will expire in the next 3 days?"
• "What are the top 5 selling items?"
• "How much profit did we make from milk sales?"

Type 'help' anytime for this message.
Type 'language' to change language.""",
        'language_changed': "✅ Language changed to English!",
        'processing': "Processing your query...",
        'error': "Sorry, I encountered an error. Please try again."
    },
    'hi': {
        'welcome': """🤖 *Sales Analytics Bot*

अपनी पसंदीदा भाषा चुनें / Choose your preferred language:

1️⃣ *English* - Continue in English
2️⃣ *हिंदी* - हिंदी में जारी रखें

भाषा चुनने के लिए 1 या 2 का जवाब दें।""",
        'help': """🤖 *Sales Analytics Bot*

अपने बिक्री डेटा के बारे में सवाल पूछें! यहाँ कुछ उदाहरण हैं:

• "पिछले हफ्ते सबसे ज्यादा क्या बिका?"
• "इस महीने का कुल मुनाफा कितना है?"
• "अगले 3 दिनों में कौन सी चीजें एक्सपायर हो रही हैं?"
• "टॉप 5 बिकने वाली चीजें कौन सी हैं?"
• "दूध की बिक्री से कितना मुनाफा हुआ?"

किसी भी समय 'help' टाइप करें।
भाषा बदलने के लिए 'language' टाइप करें।""",
        'language_changed': "✅ भाषा हिंदी में बदल दी गई!",
        'processing': "आपका सवाल प्रोसेस हो रहा है...",
        'error': "माफ़ करें, एक त्रुटि आई। कृपया फिर से कोशिश करें।"
    }
}

def get_user_language(user_id):
    """Get user's preferred language"""
    return user_languages.get(user_id, 'en')

def set_user_language(user_id, language):
    """Set user's preferred language"""
    user_languages[user_id] = language

def get_message(key, language='en'):
    """Get localized message"""
    return MESSAGES.get(language, MESSAGES['en']).get(key, MESSAGES['en'][key])

def process_query_simple(query, language='en'):
    """Simple query processing without AI (for testing)"""
    try:
        # Simple keyword-based responses
        query_lower = query.lower()
        
        if 'total' in query_lower and ('profit' in query_lower or 'मुनाफा' in query):
            if language == 'hi':
                return "कुल मुनाफा: $522.12"
            else:
                return "Total profit: $522.12"
        
        elif 'top' in query_lower or 'सबसे ज्यादा' in query:
            if language == 'hi':
                return "टॉप बिकने वाली चीजें:\n1. टमाटर (283)\n2. केले (278)\n3. मछली (200)"
            else:
                return "Top selling items:\n1. Tomatoes (283)\n2. Bananas (278)\n3. Fish (200)"
        
        elif 'milk' in query_lower or 'दूध' in query:
            if language == 'hi':
                return "दूध की बिक्री: 109 यूनिट"
            else:
                return "Milk sales: 109 units"
        
        else:
            if language == 'hi':
                return f"सवाल: {query}\n\nमैं इस सवाल का जवाब देने की कोशिश कर रहा हूं..."
            else:
                return f"Query: {query}\n\nI'm trying to answer this question..."
    
    except Exception as e:
        if language == 'hi':
            return f"त्रुटि: {str(e)}"
        else:
            return f"Error: {str(e)}"

@app.route('/')
def home():
    """Home page with basic information"""
    return jsonify({
        "message": "Sales Analytics Bot - Language Test Mode",
        "status": "running",
        "endpoints": {
            "test_query": "/test-query",
            "health": "/health",
            "language": "/language"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/language', methods=['POST'])
def set_language():
    """Set user language preference"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        language = data.get('language', 'en')
        
        if language not in ['en', 'hi']:
            return jsonify({"error": "Language must be 'en' or 'hi'"}), 400
        
        set_user_language(user_id, language)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "language": language,
            "message": get_message('language_changed', language)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-query', methods=['POST'])
def test_query():
    """Test endpoint for queries with language support"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Please provide a 'query' in the request body"}), 400
        
        # Get user's language preference
        user_lang = get_user_language(user_id)
        
        logger.info(f"Processing query in {user_lang}: {query}")
        
        # Process the query
        response = process_query_simple(query, user_lang)
        
        return jsonify({
            "user_id": user_id,
            "language": user_lang,
            "query": query,
            "response": response,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sample-questions/<language>')
def sample_questions(language):
    """Get sample questions in specified language"""
    questions = {
        'en': [
            "Which item sold the most last week?",
            "What is the total profit for this month?",
            "Which items will expire in the next 3 days?",
            "What are the top 5 selling items?",
            "How much profit did we make from milk sales?"
        ],
        'hi': [
            "पिछले हफ्ते सबसे ज्यादा क्या बिका?",
            "इस महीने का कुल मुनाफा कितना है?",
            "अगले 3 दिनों में कौन सी चीजें एक्सपायर हो रही हैं?",
            "टॉप 5 बिकने वाली चीजें कौन सी हैं?",
            "दूध की बिक्री से कितना मुनाफा हुआ?"
        ]
    }
    
    return jsonify({
        "language": language,
        "questions": questions.get(language, questions['en'])
    })

if __name__ == '__main__':
    # Create database and sample data
    create_database()
    logger.info("Database initialized with sample data")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=Config.DEBUG
    ) 