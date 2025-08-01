import google.generativeai as genai
import json
import os
import re

# --- Configuration ---
# Configure the API key securely.
# It's best to use an environment variable.
# from google.colab import userdata
# GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
# genai.configure(api_key=GOOGLE_API_KEY)

# Or, replace with your key for local testing (less secure)
os.environ['GOOGLE_API_KEY'] = "AIzaSyDpuQM8hE7vgn-q0nAaghNgxyzqH588uJU"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# --- Model and File Paths ---
MODEL_NAME = "gemini-1.5-pro-latest"
INVOICE_FILE_PATH = "invoice.jpg"  # IMPORTANT: Change this to your file's path

# --- Check if the file exists ---
if not os.path.exists(INVOICE_FILE_PATH):
    print(f"Error: File not found at {INVOICE_FILE_PATH}")
else:
    print("Uploading file...")
    # Upload the file to the Gemini API
    uploaded_file = genai.upload_file(path=INVOICE_FILE_PATH, display_name="Sample Invoice")
    print(f"Completed upload: {uploaded_file.name}")

    # --- Initialize the model ---
    model = genai.GenerativeModel(MODEL_NAME)

    # --- The Prompt ---
    prompt = """
    Analyze the provided invoice document. Extract the following information and provide the output in a clean JSON format.

    The fields to extract are:
    - invoice_id: The invoice number or ID.
    - vendor_name: The name of the company that sent the invoice.
    - vendor_address: The full address of the vendor.
    - customer_name: The name of the customer being billed.
    - invoice_date: The date the invoice was issued.
    - due_date: The date the payment is due.
    - total_amount: The final total amount, as a number.
    - currency: The currency of the total amount (e.g., USD, EUR, INR).
    - line_items: A list of all items, where each item is a JSON object with 'description', 'quantity', 'unit_price', and 'line_total'.

    If a field is not found, return 'null' for its value. Do not include the markdown json  syntax in your response.
    """

    # --- Generate Content ---
    print("Sending request to Gemini...")
    response = model.generate_content([prompt, uploaded_file])
            
    # --- Process the Response ---
    print("\n--- Gemini Response ---")
    try:
        # Clean up the response text by removing markdown backticks and 'json' label
        clean_json_str = re.sub(r'json\s*|\s*', '', response.text.strip(), flags=re.IGNORECASE)

        # Parse the cleaned string into a Python dictionary
        invoice_data = json.loads(clean_json_str)

        print(json.dumps(invoice_data, indent=2))

        # Example of accessing a specific field
        print(f"\nSuccessfully extracted Invoice ID: {invoice_data.get('invoice_id')}")
        print(f"Total Amount Due: {invoice_data.get('total_amount')} {invoice_data.get('currency')}")

    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing JSON from response: {e}")
        print("Raw response text:")
        print(response.text)

    # --- Clean up by deleting the uploaded file ---
    genai.delete_file(uploaded_file.name)
    print(f"\nDeleted file: {uploaded_file.name}")