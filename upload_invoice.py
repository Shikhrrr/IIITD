#!/usr/bin/env python3
"""
Upload Invoice Image Script
Uploads image.png to the invoice extraction API
"""

import requests
import json
import os

def upload_invoice_image():
    """Upload invoice image to the API"""
    
    # API endpoint
    url = "http://localhost:5002/upload-invoice"
    
    # Check if image file exists
    image_file = "image.png"
    if not os.path.exists(image_file):
        print(f"❌ Error: {image_file} not found")
        return
    
    print(f"📤 Uploading {image_file} to invoice extraction API...")
    
    try:
        # Upload the file
        with open(image_file, 'rb') as f:
            files = {'file': (image_file, f, 'image/png')}
            response = requests.post(url, files=files)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print("\n📊 Extracted Invoice Data:")
            print(json.dumps(result['extracted_data'], indent=2))
            print(f"\n🆔 Invoice ID: {result['invoice_id']}")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the invoice API is running on http://localhost:5002")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def get_invoice_summary():
    """Get invoice summary from database"""
    
    url = "http://localhost:5002/invoice-summary"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print("\n📈 Invoice Summary:")
            print(json.dumps(result['summary'], indent=2))
        else:
            print(f"❌ Failed to get summary: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting summary: {str(e)}")

if __name__ == "__main__":
    print("=== INVOICE UPLOAD SCRIPT ===")
    print()
    
    # Upload the invoice
    upload_invoice_image()
    
    print("\n" + "="*50)
    
    # Get summary
    get_invoice_summary()
    
    print("\n🎉 Invoice processing complete!") 