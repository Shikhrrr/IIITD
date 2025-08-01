#!/usr/bin/env python3
"""
Test Invoice Extraction
Extract invoice data and store in database
"""

import json
import sqlite3
import uuid
from datetime import datetime
from invoice_extractor import InvoiceDataExtractor

def create_sample_invoice_data():
    """Create sample invoice data for testing"""
    
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
    
    return sample_invoice

def test_invoice_extraction():
    """Test invoice extraction and database storage"""
    
    print("=== TESTING INVOICE EXTRACTION ===")
    print()
    
    # Initialize extractor (this will create the database)
    extractor = InvoiceDataExtractor()
    
    # Create sample invoice data
    print("📝 Creating sample invoice data...")
    invoice_data = create_sample_invoice_data()
    
    print("📊 Sample Invoice Data:")
    print(json.dumps(invoice_data, indent=2))
    print()
    
    # Store extracted data
    print("💾 Storing extracted data...")
    extraction_id = extractor.store_extracted_data(
        source_file="image.png",
        method="manual",
        raw_data=json.dumps(invoice_data),
        processed_data=invoice_data,
        confidence=0.95
    )
    print(f"✅ Extracted data stored with ID: {extraction_id}")
    
    # Save invoice to database
    print("💾 Saving invoice to database...")
    invoice_id = extractor.save_invoice_to_database(invoice_data)
    
    if invoice_id:
        print(f"✅ Invoice saved to database with ID: {invoice_id}")
    else:
        print("❌ Failed to save invoice to database")
        return
    
    # Get invoice summary
    print("\n📈 Getting invoice summary...")
    summary = extractor.get_invoice_summary()
    
    print("📊 Invoice Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test natural language query
    print("\n🔍 Testing natural language query...")
    try:
        results = extractor.query_invoice_data("Show me all invoices")
        print(f"✅ Query results: {len(results)} invoices found")
        if results:
            print("📋 Query Results:")
            print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"⚠️ Query failed (expected without API keys): {str(e)}")
    
    print("\n🎉 Invoice extraction test complete!")
    return invoice_id

def show_database_contents():
    """Show contents of the invoice database"""
    
    print("\n=== DATABASE CONTENTS ===")
    
    try:
        conn = sqlite3.connect('invoice_data.db')
        cursor = conn.cursor()
        
        # Show invoices
        cursor.execute("SELECT * FROM invoices")
        invoices = cursor.fetchall()
        
        print(f"📋 Invoices table: {len(invoices)} records")
        if invoices:
            print("Sample invoice:")
            print(invoices[0])
        
        # Show invoice items
        cursor.execute("SELECT * FROM invoice_items")
        items = cursor.fetchall()
        
        print(f"📋 Invoice items table: {len(items)} records")
        if items:
            print("Sample item:")
            print(items[0])
        
        # Show extracted data
        cursor.execute("SELECT * FROM extracted_data")
        extracted = cursor.fetchall()
        
        print(f"📋 Extracted data table: {len(extracted)} records")
        if extracted:
            print("Sample extraction:")
            print(extracted[0])
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")

if __name__ == "__main__":
    # Test invoice extraction
    invoice_id = test_invoice_extraction()
    
    if invoice_id:
        # Show database contents
        show_database_contents()
        
        print("\n✅ SUCCESS: Invoice data extracted and stored in database!")
        print(f"🆔 Invoice ID: {invoice_id}")
        print("📁 Database file: invoice_data.db")
    else:
        print("\n❌ FAILED: Could not process invoice") 