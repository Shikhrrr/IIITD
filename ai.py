import os
import requests
import json
import logging
from config import Config
from db import execute_query, get_database_schema_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIQueryProcessor:
    def __init__(self):
        self.huggingface_api_key = Config.HUGGINGFACE_API_KEY
        
        # Primary model (BharatGen AI)
        self.primary_models = [
            "CoRover/BharatGPT-3B-Indic",
            "bharatgenai/Param-1-2.9B-Instruct"
        ]
        
        # Fallback model
        self.fallback_model = "mistralai/Mistral-7B-Instruct-v0.2"
        
        # Get database schema
        self.db_schema = get_database_schema_info()
    
    def generate_sql(self, query, language='en', phone_number=None):
        """Generate SQL query using Hugging Face API"""
        # Determine language-specific context
        context = """Based on a multi-shop sales database with three tables:
        1. shops (id, name, owner_phone)
        2. items (id, shop_id, name, cost_price, selling_price, expiry_date)
        3. sales (id, item_id, quantity_sold, profit, sale_date)"""
        
        if language == 'hi':
            context = """एक मल्टी-शॉप बिक्री डेटाबेस के आधार पर जिसमें तीन टेबल हैं:
            1. shops (id, name, owner_phone)
            2. items (id, shop_id, name, cost_price, selling_price, expiry_date)
            3. sales (id, item_id, quantity_sold, profit, sale_date)"""
        
        # Add shop filtering context if phone number is provided
        shop_filter = ""
        if phone_number:
            if language == 'hi':
                shop_filter = f"\n\nफ़ोन नंबर {phone_number} से जुड़ी दुकान के लिए क्वेरी करें। shops.owner_phone = '{phone_number}' का उपयोग करके फ़िल्टर करें।"
            else:
                shop_filter = f"\n\nQuery for the shop associated with phone number {phone_number}. Filter using shops.owner_phone = '{phone_number}'."
        
        # Create prompt for SQL generation
        prompt = f"""
        {context}{shop_filter}
        
        Database Schema:
        {self.db_schema}
        
        User Question: {query}
        
        Generate ONLY a valid SQL query to answer this question. The query should include proper JOINs between tables where needed (items.shop_id = shops.id and sales.item_id = items.id). Return ONLY the SQL query without any explanations or comments.
        """
        
        # Try primary models first
        for model in self.primary_models:
            try:
                logger.info(f"Trying to generate SQL with model: {model}")
                sql = self._call_huggingface_api(prompt, model)
                if sql and "SELECT" in sql.upper():
                    logger.info(f"Successfully generated SQL with model: {model}")
                    return sql
            except Exception as e:
                logger.warning(f"Error with model {model}: {str(e)}")
        
        # Fallback to Mistral model
        try:
            logger.info(f"Falling back to model: {self.fallback_model}")
            sql = self._call_huggingface_api(prompt, self.fallback_model)
            if sql and "SELECT" in sql.upper():
                logger.info(f"Successfully generated SQL with fallback model")
                return sql
        except Exception as e:
            logger.error(f"Error with fallback model: {str(e)}")
            raise Exception(f"Failed to generate SQL query: {str(e)}")
        
        raise Exception("Failed to generate a valid SQL query")
    
    def _call_huggingface_api(self, prompt, model_name):
        """Call Hugging Face Inference API"""
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
        payload = {"inputs": prompt}
        
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # Extract SQL from response (format varies by model)
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'generated_text' in result[0]:
                    # Standard format for most models
                    sql = result[0]['generated_text']
                else:
                    # Fallback for other response formats
                    sql = str(result[0])
            elif isinstance(result, dict) and 'generated_text' in result:
                sql = result['generated_text']
            else:
                sql = str(result)
            
            # Extract just the SQL query (remove any explanations)
            if "SELECT" in sql.upper():
                # Find the first SELECT statement
                start_idx = sql.upper().find("SELECT")
                # Try to find the end of the SQL query (usually ends with a semicolon)
                end_idx = sql.find(";", start_idx)
                if end_idx != -1:
                    sql = sql[start_idx:end_idx+1].strip()
                else:
                    # If no semicolon, take the rest of the text
                    sql = sql[start_idx:].strip()
            
            return sql
        elif response.status_code == 404:
            # Model not found, will trigger fallback
            raise Exception(f"Model {model_name} not found")
        else:
            # Other API errors
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def process_query(self, user_question, language='en', phone_number=None):
        """Process natural language query and return formatted response in specified language"""
        try:
            # Language-specific prompts
            language_prompts = {
                'en': {
                    'context': "Based on a multi-shop sales database with shops, items, and sales tables",
                    'instruction': "Please provide a clear, human-readable response with relevant numbers and insights in English.",
                    'format': "Query: {question}\n\nResult: {result}"
                },
                'hi': {
                    'context': "एक मल्टी-शॉप बिक्री डेटाबेस के आधार पर जिसमें shops, items, और sales टेबल हैं",
                    'instruction': "कृपया हिंदी में स्पष्ट, पठनीय प्रतिक्रिया दें जिसमें प्रासंगिक संख्याएं और अंतर्दृष्टि हों।",
                    'format': "सवाल: {question}\n\nपरिणाम: {result}"
                }
            }
            
            prompt_config = language_prompts.get(language, language_prompts['en'])
            
            # Generate SQL query using Hugging Face API
            sql_query = self.generate_sql(user_question, language, phone_number)
            logger.info(f"Generated SQL query: {sql_query}")
            
            # Execute the query
            try:
                columns, results = execute_query(sql_query, phone_number=phone_number)
                
                # Format results as a string
                if results:
                    # Create a formatted table-like output
                    result_str = "\n"
                    # Add column headers
                    result_str += " | ".join(columns) + "\n"
                    result_str += "-" * (sum(len(col) for col in columns) + 3 * (len(columns) - 1)) + "\n"
                    
                    # Add rows
                    for row in results:
                        # Convert row to string values, handling dictionaries (for nested JSON from Supabase)
                        row_values = []
                        for cell in row:
                            if isinstance(cell, dict):
                                # For nested objects like foreign key references
                                row_values.append(str(cell.get('name', str(cell))))
                            else:
                                row_values.append(str(cell))
                        
                        result_str += " | ".join(row_values) + "\n"
                else:
                    result_str = "No data found for this query."
            except Exception as e:
                logger.error(f"Error executing SQL query: {str(e)}")
                if language == 'hi':
                    return f"सवाल: {user_question}\n\nSQL क्वेरी निष्पादित करते समय त्रुटि: {str(e)}"
                else:
                    return f"Query: {user_question}\n\nError executing SQL query: {str(e)}"
            
            # Format the response in the specified language
            if results:
                return prompt_config['format'].format(question=user_question, result=result_str)
            else:
                if language == 'hi':
                    return f"सवाल: {user_question}\n\nइस सवाल के लिए कोई डेटा नहीं मिला।"
                else:
                    return f"Query: {user_question}\n\nNo data found for this query."
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            if language == 'hi':
                return f"आपके सवाल को प्रोसेस करते समय एक त्रुटि आई: {str(e)}। कृपया अलग सवाल के साथ फिर से कोशिश करें।"
            else:
                return f"I encountered an error while processing your query: {str(e)}. Please try again with a different question."
    
    def get_sample_questions(self, language='en'):
        """Return sample questions in the specified language"""
        questions = {
            'en': [
                "Which item sold the most last week in my shop?",
                "What is the total profit for this month?",
                "Which items will expire in the next 3 days?",
                "What are the top 5 selling items in my store?",
                "How much profit did we make from milk sales?",
                "Show me sales data for the last 7 days",
                "Which items have the highest profit margin?",
                "What items are expiring soon?",
                "Compare selling price vs. cost price for all items",
                "What are the seasonal sales trends by month?",
                "Which items should I consider for dynamic pricing?"
            ],
            'hi': [
                "पिछले हफ्ते मेरी दुकान में सबसे ज्यादा क्या बिका?",
                "इस महीने का कुल मुनाफा कितना है?",
                "अगले 3 दिनों में कौन सी चीजें एक्सपायर हो रही हैं?",
                "मेरी दुकान में टॉप 5 बिकने वाली चीजें कौन सी हैं?",
                "दूध की बिक्री से कितना मुनाफा हुआ?",
                "पिछले 7 दिनों का बिक्री डेटा दिखाएं",
                "कौन सी चीजों का प्रॉफिट मार्जिन सबसे ज्यादा है?",
                "कौन सी चीजें जल्द एक्सपायर हो रही हैं?",
                "सभी वस्तुओं के लिए बिक्री मूल्य और लागत मूल्य की तुलना करें",
                "महीने के अनुसार मौसमी बिक्री प्रवृत्तियां क्या हैं?",
                "किन वस्तुओं के लिए मुझे डायनामिक प्राइसिंग पर विचार करना चाहिए?"
            ]
        }
        return questions.get(language, questions['en'])