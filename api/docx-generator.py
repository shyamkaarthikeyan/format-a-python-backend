"""
DOCX Generator endpoint for Python backend
Generates IEEE-formatted DOCX documents
"""

import json
import sys
import os
import base64
from io import BytesIO
from http.server import BaseHTTPRequestHandler

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
        """Handle POST requests for DOCX generation"""
        try:
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
                    'message': 'Document title is required for DOCX generation'
                })
                self.wfile.write(error_response.encode())
                return
            
            if not document_data.get('authors') or not any(author.get('name') for author in document_data.get('authors', [])):
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Missing authors',
                    'message': 'At least one author is required for DOCX generation'
                })
                self.wfile.write(error_response.encode())
                return
            
            # Generate the DOCX document
            print("Generating DOCX document...", file=sys.stderr)
            docx_buffer = generate_ieee_document(document_data)
            
            if not docx_buffer or docx_buffer.getvalue() == b'':
                raise Exception("Generated DOCX document is empty")
            
            # Convert to base64 for JSON response
            docx_base64 = base64.b64encode(docx_buffer.getvalue()).decode('utf-8')
            
            print(f"DOCX generated successfully, size: {len(docx_buffer.getvalue())} bytes", file=sys.stderr)
            
            self.end_headers()
            response = json.dumps({
                'success': True,
                'file_data': docx_base64,
                'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'file_size': len(docx_buffer.getvalue()),
                'message': 'DOCX document generated successfully'
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
            print(f"DOCX generation failed: {e}", file=sys.stderr)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'DOCX generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())