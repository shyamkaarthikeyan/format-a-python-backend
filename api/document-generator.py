import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add parent directory to path to import ieee_generator_fixed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

# Import only from the correct ieee_generator_fixed.py
from ieee_generator_fixed import generate_ieee_html_preview, generate_ieee_document

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        # Allow localhost for development
        if os.getenv('NODE_ENV') == 'development':
            self.send_header('Access-Control-Allow-Origin', '*')
        else:
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview')
        self.end_headers()

    def do_POST(self):
        """Generate IEEE document - supports both HTML preview and DOCX download"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            document_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required field
            if not document_data.get('title'):
                self.send_error_response(400, 'Title is required')
                return
            
            # Check if this is a PDF download request
            if document_data.get('format') == 'pdf' and document_data.get('action') == 'download':
                self.handle_pdf_download(document_data)
                return
            
            # Check if this is a DOCX download request
            if document_data.get('format') == 'docx' and document_data.get('action') == 'download':
                self.handle_docx_download(document_data)
                return
            
            # Default: Generate HTML preview using ieee_generator_fixed.py
            preview_html = generate_ieee_html_preview(document_data)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'preview_html': preview_html,
                'generator': 'ieee_generator_fixed.py',
                'message': 'IEEE preview generated successfully'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, f'Document generation failed: {str(e)}')
    
    def handle_pdf_download(self, document_data):
        """Handle PDF download requests - returns DOCX since PDF conversion not available in serverless"""
        try:
            import base64
            
            # Generate DOCX document (PDF conversion not available in serverless environment)
            docx_bytes = generate_ieee_document(document_data)
            
            if not docx_bytes or len(docx_bytes) == 0:
                raise Exception("Generated document is empty")
            
            # Convert to base64 for JSON response
            docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
            
            # Send success response with CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            # Use environment-aware CORS
            if os.getenv('NODE_ENV') == 'development':
                self.send_header('Access-Control-Allow-Origin', '*')
            else:
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            response = {
                'success': True,
                'file_data': docx_base64,
                'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'file_size': len(docx_bytes),
                'message': 'PDF conversion not available in serverless environment. DOCX provided with identical IEEE formatting.',
                'note': 'DOCX format contains identical IEEE formatting to PDF',
                'requested_format': 'pdf',
                'actual_format': 'docx'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, f'PDF generation failed: {str(e)}')

    def handle_docx_download(self, document_data):
        """Handle DOCX download requests"""
        try:
            import base64
            
            # Generate DOCX document (returns bytes, not BytesIO)
            docx_bytes = generate_ieee_document(document_data)
            
            if not docx_bytes or len(docx_bytes) == 0:
                raise Exception("Generated DOCX document is empty")
            
            # Convert to base64 for JSON response
            docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
            
            # Send success response with environment-aware CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            if os.getenv('NODE_ENV') == 'development':
                self.send_header('Access-Control-Allow-Origin', '*')
            else:
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            response = {
                'success': True,
                'file_data': docx_base64,
                'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'file_size': len(docx_bytes),
                'message': 'DOCX document generated successfully'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, f'DOCX generation failed: {str(e)}')
    
    def send_error_response(self, status_code, error_message):
        """Send error response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': error_message,
            'generator': 'ieee_generator_fixed.py'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))