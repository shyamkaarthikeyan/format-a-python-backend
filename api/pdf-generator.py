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
        # Allow localhost for development
        if os.getenv('NODE_ENV') == 'development':
            self.send_header('Access-Control-Allow-Origin', '*')
        else:
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
            # Use environment-aware CORS
            if os.getenv('NODE_ENV') == 'development':
                self.send_header('Access-Control-Allow-Origin', '*')
            else:
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
            
            # Always return DOCX for now (PDF conversion disabled in serverless)
            # This provides identical IEEE formatting as documented
            file_data = base64.b64encode(docx_buffer.getvalue()).decode('utf-8')
            file_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            
            # Provide clear message about format
            if is_preview:
                message = 'Preview generated successfully. DOCX format contains identical IEEE formatting to PDF.'
            else:
                message = 'Document generated successfully. DOCX format contains identical IEEE formatting to PDF.'
            
            print(f"Document generated successfully, size: {len(docx_buffer.getvalue())} bytes", file=sys.stderr)
            
            # Record download in database if not a preview
            download_recorded = False
            if not is_preview:
                try:
                    # Import database utilities
                    sys.path.insert(0, parent_dir)
                    from db_utils import record_download
                    
                    # Extract user info from request headers if available
                    user_agent = self.headers.get('User-Agent', 'Unknown')
                    
                    # Record the download
                    download_data = {
                        'document_title': document_data.get('title', 'Untitled Document'),
                        'file_format': 'pdf',  # Even if we return DOCX, user requested PDF
                        'file_size': len(docx_buffer.getvalue()),
                        'user_agent': user_agent,
                        'ip_address': self.headers.get('X-Forwarded-For', self.client_address[0]),
                        'document_metadata': {
                            'authors': [author.get('name', '') for author in document_data.get('authors', [])],
                            'sections': len(document_data.get('sections', [])),
                            'references': len(document_data.get('references', [])),
                            'generated_by': 'python_backend',
                            'requested_format': 'pdf',
                            'actual_format': 'docx' if 'DOCX' in message else 'pdf'
                        }
                    }
                    
                    # Try to get user ID from authorization header
                    auth_header = self.headers.get('Authorization', '')
                    if auth_header.startswith('Bearer '):
                        try:
                            import jwt
                            token = auth_header.replace('Bearer ', '')
                            # Note: We'd need the JWT secret to decode, but for now we'll skip user association
                            # The frontend should still call record-download with proper user context
                        except:
                            pass
                    
                    # Record download in database (backend audit trail)
                    print("Recording download in database...", file=sys.stderr)
                    try:
                        record_download(download_data)
                        download_recorded = True
                        print("✅ Download recorded successfully in backend", file=sys.stderr)
                    except Exception as record_error:
                        print(f"⚠️ Backend download recording failed: {record_error}", file=sys.stderr)
                        download_recorded = False
                    
                except Exception as db_error:
                    print(f"Failed to record download in database: {db_error}", file=sys.stderr)
                    # Don't fail the request if database recording fails
            
            self.end_headers()
            response = json.dumps({
                'success': True,
                'file_data': file_data,
                'file_type': file_type,
                'file_size': len(docx_buffer.getvalue()),
                'is_preview': is_preview,
                'message': message,
                'note': 'DOCX format contains identical IEEE formatting to PDF',
                'download_recorded': download_recorded
            })
            self.wfile.write(response.encode())
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            # Use environment-aware CORS
            if os.getenv('NODE_ENV') == 'development':
                self.send_header('Access-Control-Allow-Origin', '*')
            else:
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
            # Use environment-aware CORS
            if os.getenv('NODE_ENV') == 'development':
                self.send_header('Access-Control-Allow-Origin', '*')
            else:
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'PDF generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())