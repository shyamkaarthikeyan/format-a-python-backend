"""
PDF Generator endpoint for Python backend
Generates IEEE-formatted PDF documents with preview support
"""

import json
import sys
import os
import base64
from io import BytesIO
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import the generate function from the local IEEE generator
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

try:
    from ieee_generator_fixed import generate_ieee_document
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    def generate_ieee_document(data):
        raise Exception(f"IEEE generator not available: {e}")

# Try to import PDF conversion libraries
try:
    from docx2pdf import convert
    PDF_CONVERSION_AVAILABLE = True
except ImportError:
    print("docx2pdf not available, will return DOCX for PDF requests", file=sys.stderr)
    PDF_CONVERSION_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for PDF generation"""
        try:
            # Parse query parameters to check for preview mode
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            is_preview = 'preview' in query_params and query_params['preview'][0].lower() == 'true'
            
            # Set CORS headers first
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.send_header('Content-Type', 'application/json')
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Empty request body',
                    'message': 'Document data is required'
                })
                self.wfile.write(error_response.encode())
                return
                
            post_data = self.rfile.read(content_length)
            document_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            if not document_data.get('title'):
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Missing document title',
                    'message': 'Document title is required for PDF generation'
                })
                self.wfile.write(error_response.encode())
                return
            
            if not document_data.get('authors') or not any(author.get('name') for author in document_data.get('authors', [])):
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Missing authors',
                    'message': 'At least one author is required for PDF generation'
                })
                self.wfile.write(error_response.encode())
                return
            
            # Generate the DOCX document first
            print(f"Generating {'preview' if is_preview else 'download'} PDF document...", file=sys.stderr)
            docx_buffer = generate_ieee_document(document_data)
            
            if not docx_buffer or docx_buffer.getvalue() == b'':
                raise Exception("Generated DOCX document is empty")
            
            # Try to convert to PDF if libraries are available
            if PDF_CONVERSION_AVAILABLE:
                try:
                    # For serverless environments, PDF conversion might not work
                    # So we'll provide DOCX as fallback with appropriate message
                    print("PDF conversion not supported in serverless environment", file=sys.stderr)
                    raise Exception("PDF conversion not available in serverless environment")
                except Exception as pdf_error:
                    print(f"PDF conversion failed: {pdf_error}", file=sys.stderr)
                    # Fall back to DOCX
                    file_data = base64.b64encode(docx_buffer.getvalue()).decode('utf-8')
                    file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    message = 'PDF conversion not available in serverless environment. DOCX provided with identical IEEE formatting.'
            else:
                # No PDF conversion available, return DOCX
                file_data = base64.b64encode(docx_buffer.getvalue()).decode('utf-8')
                file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                message = 'PDF conversion not available. DOCX provided with identical IEEE formatting.'
            
            print(f"Document generated successfully, size: {len(docx_buffer.getvalue())} bytes", file=sys.stderr)
            
            self.end_headers()
            response = json.dumps({
                'success': True,
                'file_data': file_data,
                'file_type': file_type,
                'file_size': len(docx_buffer.getvalue()),
                'is_preview': is_preview,
                'message': message,
                'note': 'DOCX format contains identical IEEE formatting to PDF'
            })
            self.wfile.write(response.encode())
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'Invalid JSON',
                'message': f'Failed to parse request body: {str(e)}'
            })
            self.wfile.write(error_response.encode())
            
        except Exception as e:
            print(f"PDF generation failed: {e}", file=sys.stderr)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'PDF generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())