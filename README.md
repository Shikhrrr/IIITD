# WhatsApp Sales Analytics Bot

A Python Flask application that integrates Twilio WhatsApp, SQLite database, and OpenAI with LangChain to provide natural language querying of sales data via WhatsApp.

## Features

- 🤖 **WhatsApp Integration**: Receive and respond to messages via Twilio WhatsApp Sandbox
- 📊 **Sales Analytics**: Query sales data using natural language
- 🧠 **AI-Powered**: Uses OpenAI GPT-4o-mini with LangChain for intelligent responses
- 💾 **SQLite Database**: Local database with sample sales data
- 🔄 **Real-time Processing**: Instant responses to WhatsApp queries

## Prerequisites

- Python 3.8 or higher
- Twilio account with WhatsApp Sandbox access
- OpenAI API key
- ngrok (for exposing local server to internet)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` file with your actual credentials:
   ```env
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   TWILIO_WHATSAPP_NUMBER=+14155238886
   
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

## Setup Instructions

### 1. Twilio WhatsApp Sandbox Setup

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to Messaging → Try it out → Send a WhatsApp message
3. Follow the instructions to join your WhatsApp Sandbox
4. Note your Twilio WhatsApp number (usually +14155238886)

### 2. OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add the API key to your `.env` file

### 3. Run the Application

1. **Start the Flask application**:
   ```bash
   python app.py
   ```
   
   The app will:
   - Create a SQLite database (`sales.db`) with sample data
   - Start the Flask server on `http://localhost:5000`

2. **Expose your local server using ngrok**:
   ```bash
   ngrok http 5000
   ```
   
   This will give you a public URL like `https://abc123.ngrok.io`

3. **Configure Twilio Webhook**:
   - Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings
   - Set the webhook URL to: `https://your-ngrok-url.ngrok.io/whatsapp`
   - Set HTTP method to POST

## Usage

### WhatsApp Commands

Send these messages to your Twilio WhatsApp number:

- **`help`** - Show help message with examples
- **`examples`** - Show sample questions you can ask
- **Natural language queries** like:
  - "Which item sold the most last week?"
  - "What is the total profit for this month?"
  - "Which items will expire in the next 3 days?"
  - "What are the top 5 selling items?"
  - "How much profit did we make from milk sales?"

### Sample Questions

The bot can answer questions about:
- Sales performance by item
- Profit analysis
- Expiry date tracking
- Top-selling products
- Time-based sales data
- Product-specific analytics

## Project Structure

```
├── app.py              # Main Flask application with webhooks
├── ai.py               # OpenAI and LangChain integration
├── db.py               # Database connection and sample data
├── config.py           # Environment variables and configuration
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables template
├── README.md          # This file
└── sales.db           # SQLite database (created automatically)
```

## Database Schema

The `sales.db` database contains a `sales` table with columns:
- `id` - Primary key
- `item_name` - Name of the product
- `quantity_sold` - Number of units sold
- `profit` - Profit per sale
- `expiry_date` - Product expiry date
- `sale_date` - Date of sale

## API Endpoints

- `GET /` - Home page with app information
- `GET /health` - Health check endpoint
- `POST /whatsapp` - Twilio WhatsApp webhook
- `POST /send-message` - Send test messages (for development)

## Development

### Testing Locally

1. Use the `/send-message` endpoint to test message sending:
   ```bash
   curl -X POST http://localhost:5000/send-message \
     -H "Content-Type: application/json" \
     -d '{"to": "+1234567890", "message": "Test message"}'
   ```

2. Check logs in the terminal for debugging information

### Customizing

- **Add new sample data**: Modify the `create_database()` function in `db.py`
- **Change AI model**: Update the model in `ai.py` (e.g., to `gpt-4`)
- **Add new endpoints**: Extend `app.py` with additional routes
- **Modify responses**: Customize the response formatting in `ai.py`

## Troubleshooting

### Common Issues

1. **"Invalid API Key"**: Check your OpenAI API key in `.env`
2. **"Twilio authentication failed"**: Verify your Twilio credentials
3. **"Webhook not receiving messages"**: Ensure ngrok is running and webhook URL is correct
4. **"Database not found"**: The app creates the database automatically on first run

### Debug Mode

Set `DEBUG=True` in your `.env` file to see detailed error messages and logs.

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- The Flask app runs on `0.0.0.0:5000` by default - change this for production
- Consider adding authentication for production use
- Regularly rotate your API keys

## License

This project is for educational and demonstration purposes.

## Support

For issues related to:
- **Twilio**: Check [Twilio Documentation](https://www.twilio.com/docs)
- **OpenAI**: Check [OpenAI Documentation](https://platform.openai.com/docs)
- **LangChain**: Check [LangChain Documentation](https://python.langchain.com/)
