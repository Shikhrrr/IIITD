import os
import json
import logging
from openai import OpenAI
from config import Config
from db import execute_query, get_database_schema_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIQueryProcessor:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
        # Get database schema
        self.db_schema = get_database_schema_info()
    
    def generate_sql(self, query, language='en', phone_number=None):
        """Generate SQL query using OpenAI API"""
        if not self.client:
            raise Exception("OpenAI API key not configured")
        
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
        
        try:
            logger.info("Generating SQL with OpenAI")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only valid SQL queries without any explanations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql = response.choices[0].message.content.strip()
            if sql and "SELECT" in sql.upper():
                logger.info("Successfully generated SQL with OpenAI")
                return sql
            else:
                raise Exception("Generated response is not a valid SQL query")
                
        except Exception as e:
            logger.error(f"Error generating SQL with OpenAI: {str(e)}")
            raise Exception(f"Failed to generate SQL query: {str(e)}")
    
    def process_query(self, user_question, language='en', phone_number=None):
        """Process a natural language query and return results"""
        try:
            logger.info(f"Processing query: {user_question} (language: {language})")
            
            # Generate SQL from natural language
            sql_query = self.generate_sql(user_question, language, phone_number)
            logger.info(f"Generated SQL: {sql_query}")
            
            # Execute the SQL query
            columns, results = execute_query(sql_query, phone_number=phone_number)
            
            # Format the results
            if not results:
                if language == 'hi':
                    return "कोई परिणाम नहीं मिला।"
                else:
                    return "No results found."
            
            # Format results as a readable response
            response = self._format_results(columns, results, language)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            if language == 'hi':
                return f"माफ़ करें, एक त्रुटि आई: {str(e)}"
            else:
                return f"Sorry, an error occurred: {str(e)}"
    
    def _format_results(self, columns, results, language='en'):
        """Format query results into a readable response"""
        try:
            if not results:
                if language == 'hi':
                    return "कोई परिणाम नहीं मिला।"
                else:
                    return "No results found."
            
            # For simple queries, format nicely
            if len(columns) <= 3 and len(results) <= 10:
                response_lines = []
                
                if language == 'hi':
                    response_lines.append("📊 *परिणाम:*")
                else:
                    response_lines.append("📊 *Results:*")
                
                for i, row in enumerate(results, 1):
                    line_parts = []
                    for col, val in zip(columns, row):
                        if isinstance(val, float):
                            val = f"{val:.2f}"
                        line_parts.append(f"{col}: {val}")
                    response_lines.append(f"{i}. {' | '.join(line_parts)}")
                
                return "\n".join(response_lines)
            
            # For complex queries, provide summary
            else:
                if language == 'hi':
                    return f"📊 {len(results)} परिणाम मिले। पहले कुछ परिणाम:\n" + \
                           "\n".join([f"{i+1}. {', '.join([str(val) for val in row[:3]])}..." 
                                     for i, row in enumerate(results[:5])])
                else:
                    return f"📊 Found {len(results)} results. First few results:\n" + \
                           "\n".join([f"{i+1}. {', '.join([str(val) for val in row[:3]])}..." 
                                     for i, row in enumerate(results[:5])])
                    
        except Exception as e:
            logger.error(f"Error formatting results: {str(e)}")
            if language == 'hi':
                return f"परिणाम प्रारूपित करने में त्रुटि: {str(e)}"
            else:
                return f"Error formatting results: {str(e)}"
    
    def get_sample_questions(self, language='en'):
        """Get sample questions for the user"""
        if language == 'hi':
            return [
                "पिछले हफ्ते सबसे ज्यादा क्या बिका?",
                "इस महीने का कुल मुनाफा कितना है?",
                "अगले 3 दिनों में कौन सी चीजें एक्सपायर हो रही हैं?",
                "टॉप 5 बिकने वाली चीजें कौन सी हैं?",
                "दूध की बिक्री से कितना मुनाफा हुआ?"
            ]
        else:
            return [
                "Which item sold the most last week?",
                "What is the total profit for this month?",
                "Which items will expire in the next 3 days?",
                "What are the top 5 selling items?",
                "How much profit did we make from milk sales?"
            ]