from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from config import Config
from db import create_database
from ai import AIQueryProcessor
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Twilio client
twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

# Initialize AI processor
ai_processor = AIQueryProcessor()

# In-memory storage for user language preferences (in production, use a database)
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

def get_user_language(from_number):
    """Get user's preferred language"""
    return user_languages.get(from_number, 'en')

def set_user_language(from_number, language):
    """Set user's preferred language"""
    user_languages[from_number] = language

def get_message(key, language='en'):
    """Get localized message"""
    return MESSAGES.get(language, MESSAGES['en']).get(key, MESSAGES['en'][key])

@app.route('/')
def home():
    """Home page with basic information"""
    return jsonify({
        "message": "WhatsApp Sales Analytics Bot",
        "status": "running",
        "endpoints": {
            "webhook": "/whatsapp",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get the message from the request
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"Received message from {from_number}: {incoming_msg}")
        
        # Create Twilio response
        resp = MessagingResponse()
        msg = resp.message()
        
        # Get user's language preference
        user_lang = get_user_language(from_number)
        
        # Handle different types of messages
        if not incoming_msg:
            msg.body(get_message('welcome', user_lang))
            return str(resp)
        
        # Language selection
        if incoming_msg in ['1', '2']:
            selected_lang = 'en' if incoming_msg == '1' else 'hi'
            set_user_language(from_number, selected_lang)
            msg.body(get_message('language_changed', selected_lang))
            return str(resp)
        
        # Language change command
        if incoming_msg.lower() in ['language', 'भाषा', 'lang']:
            msg.body(get_message('welcome', user_lang))
            return str(resp)
        
        # Help command
        if incoming_msg.lower() in ['help', 'h', '?', 'मदद']:
            msg.body(get_message('help', user_lang))
            return str(resp)
        
        # Sample questions command
        if incoming_msg.lower() in ['examples', 'sample', 'samples', 'उदाहरण']:
            sample_questions = ai_processor.get_sample_questions(user_lang)
            if user_lang == 'hi':
                examples_text = "📋 *उदाहरण सवाल:*\n\n" + "\n".join([f"• {q}" for q in sample_questions[:5]])
            else:
                examples_text = "📋 *Sample Questions:*\n\n" + "\n".join([f"• {q}" for q in sample_questions[:5]])
            msg.body(examples_text)
            return str(resp)
        
        # Process the query with AI (with language preference)
        logger.info(f"Processing query in {user_lang}: {incoming_msg}")
        response = ai_processor.process_query(incoming_msg, user_lang)
        
        # Send the response
        msg.body(response)
        
        logger.info(f"Sent response to {from_number} in {user_lang}")
        return str(resp)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")
        resp = MessagingResponse()
        msg = resp.message()
        user_lang = get_user_language(from_number) if 'from_number' in locals() else 'en'
        msg.body(get_message('error', user_lang))
        return str(resp)

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send a message to a WhatsApp number (for testing)"""
    try:
        data = request.get_json()
        to_number = data.get('to')
        message = data.get('message')
        
        if not to_number or not message:
            return jsonify({"error": "Missing 'to' or 'message' parameter"}), 400
        
        # Send message via Twilio
        message = twilio_client.messages.create(
            from_=f'whatsapp:{Config.TWILIO_WHATSAPP_NUMBER}',
            body=message,
            to=f'whatsapp:{to_number}'
        )
        
        return jsonify({
            "success": True,
            "message_sid": message.sid,
            "status": message.status
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
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