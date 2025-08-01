import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvoiceDataExtractor:
    def __init__(self):
        self.gemini_api_key = Config.GEMINI_API_KEY
        self.openai_api_key = Config.OPENAI_API_KEY
        
        # Initialize Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
            
        # Initialize OpenAI
        self.openai_client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
        # Database file
        self.db_file = 'invoice_data.db'
        self.create_invoice_database()
    
    def create_invoice_database(self):
        """Create the invoice database with schema"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create invoices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id TEXT PRIMARY KEY,
                    invoice_number TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    customer_name TEXT,
                    customer_email TEXT,
                    customer_phone TEXT,
                    customer_address TEXT,
                    total_amount REAL,
                    tax_amount REAL,
                    discount_amount REAL,
                    subtotal REAL,
                    currency TEXT DEFAULT 'USD',
                    payment_status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create invoice_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id TEXT PRIMARY KEY,
                    invoice_id TEXT REFERENCES invoices(id),
                    item_name TEXT,
                    description TEXT,
                    quantity REAL,
                    unit_price REAL,
                    total_price REAL,
                    tax_rate REAL DEFAULT 0.0,
                    discount_rate REAL DEFAULT 0.0
                )
            ''')
            
            # Create extracted_data table for raw extraction results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extracted_data (
                    id TEXT PRIMARY KEY,
                    source_file TEXT,
                    extraction_method TEXT,
                    raw_data TEXT,
                    processed_data TEXT,
                    confidence_score REAL,
                    extraction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Invoice database created successfully")
            
        except Exception as e:
            logger.error(f"Error creating invoice database: {str(e)}")
    
    def extract_from_image(self, image_path: str) -> Dict:
        """Extract invoice data from image using Gemini"""
        try:
            if not self.gemini_model:
                raise Exception("Gemini API key not configured")
            
            # Load image
            image = genai.types.Image.from_file(image_path)
            
            # Create prompt for invoice extraction
            prompt = """
            Extract invoice data from this image and return it in the following JSON format:
            {
                "invoice_number": "string",
                "invoice_date": "YYYY-MM-DD",
                "due_date": "YYYY-MM-DD",
                "customer_name": "string",
                "customer_email": "string",
                "customer_phone": "string",
                "customer_address": "string",
                "total_amount": number,
                "tax_amount": number,
                "discount_amount": number,
                "subtotal": number,
                "currency": "string",
                "payment_status": "string",
                "payment_method": "string",
                "notes": "string",
                "items": [
                    {
                        "item_name": "string",
                        "description": "string",
                        "quantity": number,
                        "unit_price": number,
                        "total_price": number,
                        "tax_rate": number,
                        "discount_rate": number
                    }
                ]
            }
            
            Extract all available information. If any field is not found, use null or empty string.
            """
            
            # Generate response
            response = self.gemini_model.generate_content([prompt, image])
            
            # Parse JSON response
            extracted_data = json.loads(response.text)
            
            # Store raw extraction
            self.store_extracted_data(image_path, "gemini", response.text, extracted_data, 0.9)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting from image with Gemini: {str(e)}")
            # Fallback to OpenAI if Gemini fails
            return self.extract_with_openai_fallback(image_path)
    
    def extract_with_openai_fallback(self, image_path: str) -> Dict:
        """Extract invoice data using OpenAI as fallback"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            # Read image as base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt for OpenAI
            prompt = """
            Extract invoice data from this image and return it in the following JSON format:
            {
                "invoice_number": "string",
                "invoice_date": "YYYY-MM-DD",
                "due_date": "YYYY-MM-DD",
                "customer_name": "string",
                "customer_email": "string",
                "customer_phone": "string",
                "customer_address": "string",
                "total_amount": number,
                "tax_amount": number,
                "discount_amount": number,
                "subtotal": number,
                "currency": "string",
                "payment_status": "string",
                "payment_method": "string",
                "notes": "string",
                "items": [
                    {
                        "item_name": "string",
                        "description": "string",
                        "quantity": number,
                        "unit_price": number,
                        "total_price": number,
                        "tax_rate": number,
                        "discount_rate": number
                    }
                ]
            }
            
            Extract all available information. If any field is not found, use null or empty string.
            """
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting invoice data from images. Return only valid JSON."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse JSON response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Store raw extraction
            self.store_extracted_data(image_path, "openai", response.choices[0].message.content, extracted_data, 0.8)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting with OpenAI: {str(e)}")
            return {}
    
    def store_extracted_data(self, source_file: str, method: str, raw_data: str, processed_data: Dict, confidence: float):
        """Store extracted data in database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            import uuid
            extraction_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO extracted_data (id, source_file, extraction_method, raw_data, processed_data, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                extraction_id,
                source_file,
                method,
                raw_data,
                json.dumps(processed_data),
                confidence
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Extracted data stored with ID: {extraction_id}")
            
        except Exception as e:
            logger.error(f"Error storing extracted data: {str(e)}")
    
    def save_invoice_to_database(self, invoice_data: Dict) -> str:
        """Save extracted invoice data to database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            import uuid
            invoice_id = str(uuid.uuid4())
            
            # Insert invoice
            cursor.execute('''
                INSERT INTO invoices (
                    id, invoice_number, invoice_date, due_date, customer_name, customer_email,
                    customer_phone, customer_address, total_amount, tax_amount, discount_amount,
                    subtotal, currency, payment_status, payment_method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_id,
                invoice_data.get('invoice_number'),
                invoice_data.get('invoice_date'),
                invoice_data.get('due_date'),
                invoice_data.get('customer_name'),
                invoice_data.get('customer_email'),
                invoice_data.get('customer_phone'),
                invoice_data.get('customer_address'),
                invoice_data.get('total_amount', 0),
                invoice_data.get('tax_amount', 0),
                invoice_data.get('discount_amount', 0),
                invoice_data.get('subtotal', 0),
                invoice_data.get('currency', 'USD'),
                invoice_data.get('payment_status', 'pending'),
                invoice_data.get('payment_method'),
                invoice_data.get('notes')
            ))
            
            # Insert invoice items
            items = invoice_data.get('items', [])
            for item in items:
                item_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO invoice_items (
                        id, invoice_id, item_name, description, quantity, unit_price,
                        total_price, tax_rate, discount_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id,
                    invoice_id,
                    item.get('item_name'),
                    item.get('description'),
                    item.get('quantity', 0),
                    item.get('unit_price', 0),
                    item.get('total_price', 0),
                    item.get('tax_rate', 0),
                    item.get('discount_rate', 0)
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Invoice saved to database with ID: {invoice_id}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Error saving invoice to database: {str(e)}")
            return None
    
    def query_invoice_data(self, query: str) -> List[Dict]:
        """Query invoice data using natural language"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            # Get database schema
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get table schemas
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
            schemas = cursor.fetchall()
            
            # Create prompt for SQL generation
            prompt = f"""
            Based on the following database schema:
            {schemas}
            
            Generate a SQL query to answer this question: {query}
            
            The database contains invoice data with tables: invoices, invoice_items, extracted_data
            
            Return ONLY the SQL query, no explanations.
            """
            
            # Generate SQL query
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only valid SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Execute the query
            cursor.execute(sql_query)
            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            
            conn.close()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in results]
            
        except Exception as e:
            logger.error(f"Error querying invoice data: {str(e)}")
            return []
    
    def get_invoice_summary(self) -> Dict:
        """Get summary statistics of invoice data"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Get total invoices
            cursor.execute("SELECT COUNT(*) FROM invoices")
            total_invoices = cursor.fetchone()[0]
            
            # Get total amount
            cursor.execute("SELECT SUM(total_amount) FROM invoices")
            total_amount = cursor.fetchone()[0] or 0
            
            # Get payment status distribution
            cursor.execute("SELECT payment_status, COUNT(*) FROM invoices GROUP BY payment_status")
            payment_status = dict(cursor.fetchall())
            
            # Get recent invoices
            cursor.execute("""
                SELECT invoice_number, customer_name, total_amount, payment_status, invoice_date 
                FROM invoices 
                ORDER BY invoice_date DESC 
                LIMIT 5
            """)
            recent_invoices = cursor.fetchall()
            
            conn.close()
            
            return {
                "total_invoices": total_invoices,
                "total_amount": total_amount,
                "payment_status_distribution": payment_status,
                "recent_invoices": recent_invoices
            }
            
        except Exception as e:
            logger.error(f"Error getting invoice summary: {str(e)}")
            return {}

# Example usage
if __name__ == "__main__":
    extractor = InvoiceDataExtractor()
    
    # Example: Extract from image
    # invoice_data = extractor.extract_from_image("invoice.jpg")
    # invoice_id = extractor.save_invoice_to_database(invoice_data)
    
    # Example: Query data
    # results = extractor.query_invoice_data("Show me all invoices with total amount greater than 1000")
    
    # Example: Get summary
    # summary = extractor.get_invoice_summary()
    # print(summary) 