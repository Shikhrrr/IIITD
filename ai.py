import os
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from config import Config
from db import get_database_connection

class AIQueryProcessor:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        # Create SQLDatabase instance
        self.db = SQLDatabase.from_uri("sqlite:///sales.db")
        
        # Create SQL query chain
        self.query_chain = create_sql_query_chain(self.llm, self.db)
    
    def process_query(self, user_question, language='en'):
        """Process natural language query and return formatted response in specified language"""
        try:
            # Language-specific prompts
            language_prompts = {
                'en': {
                    'context': "Based on the sales database with columns: item_name, quantity_sold, profit, expiry_date, sale_date",
                    'instruction': "Please provide a clear, human-readable response with relevant numbers and insights in English.",
                    'format': "Query: {question}\n\nResult: {result}"
                },
                'hi': {
                    'context': "बिक्री डेटाबेस के आधार पर जिसमें कॉलम हैं: item_name, quantity_sold, profit, expiry_date, sale_date",
                    'instruction': "कृपया हिंदी में स्पष्ट, पठनीय प्रतिक्रिया दें जिसमें प्रासंगिक संख्याएं और अंतर्दृष्टि हों।",
                    'format': "सवाल: {question}\n\nपरिणाम: {result}"
                }
            }
            
            prompt_config = language_prompts.get(language, language_prompts['en'])
            
            # Add context about the database schema
            enhanced_question = f"""
            {prompt_config['context']}
            Answer this question: {user_question}
            
            {prompt_config['instruction']}
            """
            
            # Generate SQL query
            sql_query = self.query_chain.invoke({"question": enhanced_question})
            
            # Execute the query
            result = self.db.run(sql_query)
            
            # Format the response in the specified language
            if result:
                return prompt_config['format'].format(question=user_question, result=result)
            else:
                if language == 'hi':
                    return f"सवाल: {user_question}\n\nइस सवाल के लिए कोई डेटा नहीं मिला।"
                else:
                    return f"Query: {user_question}\n\nNo data found for this query."
            
        except Exception as e:
            if language == 'hi':
                return f"आपके सवाल को प्रोसेस करते समय एक त्रुटि आई: {str(e)}। कृपया अलग सवाल के साथ फिर से कोशिश करें।"
            else:
                return f"I encountered an error while processing your query: {str(e)}. Please try again with a different question."
    
    def get_sample_questions(self, language='en'):
        """Return sample questions in the specified language"""
        questions = {
            'en': [
                "Which item sold the most last week?",
                "What is the total profit for this month?",
                "Which items will expire in the next 3 days?",
                "What are the top 5 selling items?",
                "How much profit did we make from milk sales?",
                "Show me sales data for the last 7 days",
                "Which items have the highest profit margin?",
                "What items are expiring soon?"
            ],
            'hi': [
                "पिछले हफ्ते सबसे ज्यादा क्या बिका?",
                "इस महीने का कुल मुनाफा कितना है?",
                "अगले 3 दिनों में कौन सी चीजें एक्सपायर हो रही हैं?",
                "टॉप 5 बिकने वाली चीजें कौन सी हैं?",
                "दूध की बिक्री से कितना मुनाफा हुआ?",
                "पिछले 7 दिनों का बिक्री डेटा दिखाएं",
                "कौन सी चीजों का प्रॉफिट मार्जिन सबसे ज्यादा है?",
                "कौन सी चीजें जल्द एक्सपायर हो रही हैं?"
            ]
        }
        return questions.get(language, questions['en']) 