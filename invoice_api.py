from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from config import Config
from invoice_extractor import InvoiceDataExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize invoice extractor
invoice_extractor = InvoiceDataExtractor()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Home page with API information"""
    return jsonify({
        "message": "Invoice Data Extraction API",
        "status": "running",
        "endpoints": {
            "upload": "/upload-invoice",
            "query": "/query-invoices",
            "summary": "/invoice-summary",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/upload-invoice', methods=['POST'])
def upload_invoice():
    """Upload and extract invoice data from image"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        # Extract invoice data
        invoice_data = invoice_extractor.extract_from_image(filepath)
        
        if not invoice_data:
            return jsonify({"error": "Failed to extract invoice data"}), 500
        
        # Save to database
        invoice_id = invoice_extractor.save_invoice_to_database(invoice_data)
        
        if not invoice_id:
            return jsonify({"error": "Failed to save invoice to database"}), 500
        
        return jsonify({
            "success": True,
            "message": "Invoice data extracted and saved successfully",
            "invoice_id": invoice_id,
            "extracted_data": invoice_data
        })
        
    except Exception as e:
        logger.error(f"Error processing invoice upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/query-invoices', methods=['POST'])
def query_invoices():
    """Query invoice data using natural language"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        query = data['query']
        logger.info(f"Processing query: {query}")
        
        # Query invoice data
        results = invoice_extractor.query_invoice_data(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error querying invoices: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/invoice-summary')
def invoice_summary():
    """Get invoice summary statistics"""
    try:
        summary = invoice_extractor.get_invoice_summary()
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        logger.error(f"Error getting invoice summary: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """Extract text from image without saving to database"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Extracting text from: {filename}")
        
        # Extract invoice data (without saving to database)
        invoice_data = invoice_extractor.extract_from_image(filepath)
        
        # Clean up temporary file
        os.remove(filepath)
        
        if not invoice_data:
            return jsonify({"error": "Failed to extract invoice data"}), 500
        
        return jsonify({
            "success": True,
            "message": "Invoice data extracted successfully",
            "extracted_data": invoice_data
        })
        
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=Config.DEBUG
    ) 