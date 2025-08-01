#!/usr/bin/env python3
"""
Invoice Data Extraction Demo
This script demonstrates the invoice extraction system using Gemini and OpenAI
"""

import os
import json
import logging
from invoice_extractor import InvoiceDataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_invoice_extraction():
    """Demo the invoice extraction system"""
    print("=== INVOICE DATA EXTRACTION DEMO ===")
    print()
    
    # Initialize the extractor
    extractor = InvoiceDataExtractor()
    
    # Demo 1: Show database creation
    print("1. Database Setup:")
    print("   ✅ Invoice database created")
    print("   ✅ Tables: invoices, invoice_items, extracted_data")
    print()
    
    # Demo 2: Show sample invoice data structure
    print("2. Sample Invoice Data Structure:")
    sample_invoice = {
        "invoice_number": "INV-2024-001",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "customer_phone": "+1-555-123-4567",
        "customer_address": "123 Main St, City, State 12345",
        "total_amount": 1500.00,
        "tax_amount": 150.00,
        "discount_amount": 50.00,
        "subtotal": 1400.00,
        "currency": "USD",
        "payment_status": "pending",
        "payment_method": "credit_card",
        "notes": "Net 30 payment terms",
        "items": [
            {
                "item_name": "Web Development Services",
                "description": "Custom website development",
                "quantity": 1,
                "unit_price": 1000.00,
                "total_price": 1000.00,
                "tax_rate": 0.10,
                "discount_rate": 0.05
            },
            {
                "item_name": "SEO Optimization",
                "description": "Search engine optimization services",
                "quantity": 1,
                "unit_price": 500.00,
                "total_price": 500.00,
                "tax_rate": 0.10,
                "discount_rate": 0.00
            }
        ]
    }
    
    print("   Sample invoice data structure:")
    print(json.dumps(sample_invoice, indent=2))
    print()
    
    # Demo 3: Show extraction process
    print("3. Extraction Process:")
    print("   📸 Upload invoice image")
    print("   🤖 Gemini AI extracts data")
    print("   🔄 OpenAI fallback if needed")
    print("   💾 Store in database")
    print("   📊 Query with natural language")
    print()
    
    # Demo 4: Show API endpoints
    print("4. Available API Endpoints:")
    print("   POST /upload-invoice - Upload and extract invoice")
    print("   POST /query-invoices - Query with natural language")
    print("   GET  /invoice-summary - Get summary statistics")
    print("   POST /extract-text - Extract without saving")
    print()
    
    # Demo 5: Show query examples
    print("5. Natural Language Query Examples:")
    queries = [
        "Show me all invoices with total amount greater than 1000",
        "Find invoices for customer John Doe",
        "What is the total revenue this month?",
        "Show pending invoices",
        "List invoices with payment status 'paid'"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"   {i}. {query}")
    print()
    
    # Demo 6: Show database schema
    print("6. Database Schema:")
    print("   📋 invoices table:")
    print("      - id, invoice_number, invoice_date, due_date")
    print("      - customer_name, customer_email, customer_phone")
    print("      - total_amount, tax_amount, discount_amount")
    print("      - currency, payment_status, payment_method")
    print()
    print("   📋 invoice_items table:")
    print("      - id, invoice_id, item_name, description")
    print("      - quantity, unit_price, total_price")
    print("      - tax_rate, discount_rate")
    print()
    print("   📋 extracted_data table:")
    print("      - id, source_file, extraction_method")
    print("      - raw_data, processed_data, confidence_score")
    print()
    
    # Demo 7: Show integration features
    print("7. Integration Features:")
    print("   ✅ Gemini AI for image extraction")
    print("   ✅ OpenAI fallback for missing data")
    print("   ✅ Natural language querying")
    print("   ✅ Database storage and retrieval")
    print("   ✅ Confidence scoring")
    print("   ✅ Error handling and logging")
    print()
    
    print("=== DEMO COMPLETE ===")
    print()
    print("To use the system:")
    print("1. Set GEMINI_API_KEY in environment")
    print("2. Set OPENAI_API_KEY in environment")
    print("3. Run: python invoice_api.py")
    print("4. Upload invoice images via API")
    print("5. Query data using natural language")

def demo_api_usage():
    """Show how to use the API"""
    print("=== API USAGE EXAMPLES ===")
    print()
    
    print("1. Upload Invoice Image:")
    print("   curl -X POST http://localhost:5002/upload-invoice \\")
    print("     -F 'file=@invoice.jpg'")
    print()
    
    print("2. Query Invoice Data:")
    print("   curl -X POST http://localhost:5002/query-invoices \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"query\": \"Show me all invoices with total amount greater than 1000\"}'")
    print()
    
    print("3. Get Invoice Summary:")
    print("   curl http://localhost:5002/invoice-summary")
    print()
    
    print("4. Extract Text Only:")
    print("   curl -X POST http://localhost:5002/extract-text \\")
    print("     -F 'file=@invoice.jpg'")
    print()

if __name__ == "__main__":
    demo_invoice_extraction()
    print("\n" + "="*50 + "\n")
    demo_api_usage() 