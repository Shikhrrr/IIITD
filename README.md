# WhatsApp Sales Analytics Bot

A Python Flask application that integrates Twilio WhatsApp, Supabase (PostgreSQL) database, and BharatGen AI models via Hugging Face to provide natural language querying of sales data via WhatsApp. The application supports multiple shops and includes expiry date tracking with automated alerts.

## Features

- 🤖 **WhatsApp Integration**: Receive and respond to messages via Twilio WhatsApp Sandbox
- 📊 **Sales Analytics**: Query sales data using natural language
- 🇮🇳 **BharatGen AI**: Uses Indian AI models via Hugging Face API for intelligent responses
- 🔄 **Fallback Mechanism**: Automatically falls back to Mistral if BharatGen models are unavailable
- 🌐 **Supabase Database**: Cloud PostgreSQL database with multi-shop support
- ⏰ **Expiry Tracking**: Automated alerts for items nearing expiration
- 🏪 **Multi-Shop Support**: Filter data by shop based on owner's phone number
- 🔄 **Real-time Processing**: Instant responses to WhatsApp queries

## Prerequisites

- Python 3.8 or higher
- Twilio account with WhatsApp Sandbox access
- Hugging Face API key
- Supabase account (free tier works fine)
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
   
   # Hugging Face Configuration
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   EXPIRY_ALERT_DAYS=3
   
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

### 2. Hugging Face API Key

1. Go to [Hugging Face](https://huggingface.co/)
2. Create an account and get your API key from your profile settings
3. Add the API key to your `.env` file

The application will use BharatGen AI models (`CoRover/BharatGPT-3B-Indic` or `bharatgenai/Param-1-2.9B-Instruct`) if available, with fallback to `mistralai/Mistral-7B-Instruct-v0.2` if needed.

### 3. Supabase Setup

1. Create a Supabase account at [Supabase](https://supabase.com/)
2. Create a new project
3. Once your project is created, go to Project Settings → API
4. Copy the URL and anon/public key to your `.env` file as `SUPABASE_URL` and `SUPABASE_KEY`
5. The database schema will be automatically created when you first run the application

### 4. Run the Application

1. **Start the Flask application**:
   ```bash
   python app.py
   ```
   
   The app will:
   - Create the Supabase database schema with sample data
   - Set up a cron job for daily expiry alerts
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
- **`expiry`** - Manually trigger expiry alerts for items nearing expiration
- **`language`** or **`भाषा`** - Change language preference (English/Hindi)
- **Natural language queries** like:
  - "Which item sold the most last week?"
  - "What is the total profit for this month?"
  - "Which items will expire in the next 3 days?"
  - "What are the top 5 selling items?"
  - "How much profit did we make from milk sales?"

### Sample Questions

The bot can answer questions about:
- Sales performance by item in your shop
- Profit analysis and cost comparisons
- Expiry date tracking and alerts
- Top-selling products across time periods
- Time-based sales data and trends
- Product-specific analytics
- Inventory management
- Multi-shop comparisons (for admin users)

All queries are automatically filtered to show only data relevant to the shop associated with your phone number.

## Project Structure

```
├── app.py              # Main Flask application with webhooks
├── ai.py               # Hugging Face API integration for BharatGen AI models
├── db.py               # Supabase database connection and schema management
├── expiry_alert.py     # Expiry tracking and WhatsApp alert system
├── config.py           # Environment variables and configuration
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables template
└── README.md          # This file
```

## Database Schema

The Supabase database contains the following tables:

### `shops` table
- `id` - Primary key
- `name` - Shop name
- `owner_phone` - Phone number of shop owner (used for filtering)
- `address` - Shop address
- `created_at` - Shop creation timestamp

### `items` table
- `id` - Primary key
- `shop_id` - Foreign key to shops table
- `name` - Name of the product
- `cost_price` - Cost price of the item
- `selling_price` - Selling price of the item
- `stock_quantity` - Current stock quantity
- `expiry_date` - Product expiry date
- `created_at` - Item creation timestamp

### `sales` table
- `id` - Primary key
- `shop_id` - Foreign key to shops table
- `item_id` - Foreign key to items table
- `quantity_sold` - Number of units sold
- `sale_price` - Price at which item was sold
- `sale_date` - Date of sale
- `created_at` - Sale record creation timestamp

## API Endpoints

- `GET /` - Home page with app information
- `GET /health` - Health check endpoint
- `POST /whatsapp` - Twilio WhatsApp webhook
- `POST /send-message` - Send test messages (for development)

## Expiry Alerts

The application includes an automated system for sending expiry alerts:

- **Scheduled Alerts**: A cron job runs daily to check for items nearing expiration
- **Manual Trigger**: Send the message `expiry` to trigger alerts on demand
- **Configuration**: Set the `EXPIRY_ALERT_DAYS` environment variable to control how many days in advance to send alerts (default: 3 days)

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

- **Add new sample data**: Modify the `create_database_schema()` function in `db.py`
- **Change AI model**: Update the model in `ai.py` to use different Hugging Face models
- **Adjust expiry alerts**: Modify the `send_expiry_alerts()` function in `expiry_alert.py`
- **Add new endpoints**: Extend `app.py` with additional routes
- **Modify responses**: Customize the response formatting in `ai.py`
- **Add new shops**: Update the sample data in `db.py` to include additional shops

## Troubleshooting

### Common Issues

1. **"Invalid API Key"**: Check your Hugging Face API key in `.env`
2. **"Twilio authentication failed"**: Verify your Twilio credentials
3. **"Webhook not receiving messages"**: Ensure ngrok is running and webhook URL is correct
4. **"Supabase connection error"**: Verify your Supabase URL and key in `.env`
5. **"Permission denied"**: Ensure your Supabase policy allows the operations you're trying to perform
6. **"Cron job not running"**: Check if python-crontab is installed correctly

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
- **Hugging Face**: Check [Hugging Face Documentation](https://huggingface.co/docs)
- **BharatGen AI**: Check [BharatGPT Documentation](https://huggingface.co/CoRover/BharatGPT-3B-Indic) or [Param Documentation](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct)
