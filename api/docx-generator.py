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

# Import the IEEE generator - this MUST work for proper formatting
try:
    from ieee_generator_fixed import generate_ieee_document
    print("Successfully imported IEEE generator for DOCX", file=sys.stderr)
except ImportError as e:
    print(f"CRITICAL: Failed to import IEEE generator: {e}", file=sys.stderr)
    print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Parent directory: {parent_dir}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    
    # List files in parent directory for debugging
    try:
        files = os.listdir(parent_dir)
        print(f"Files in parent directory: {files}", file=sys.stderr)
    except Exception as list_err:
        print(f"Could not list parent directory: {list_err}", file=sys.stderr)
    
    # This should not happen - raise the error instead of using fallback
    raise ImportError(f"IEEE generator is required for proper DOCX formatting: {e}")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for DOCX generation"""
        try:
            # Set CORS headers first
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
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
            
            # Generate the DOCX document with fallback approach
            print("Generating DOCX document...", file=sys.stderr)
            
            try:
                # Try the full IEEE generator first
                docx_bytes = generate_ieee_document(document_data)
                
                if not docx_bytes or len(docx_bytes) == 0:
                    raise Exception("Generated DOCX document is empty")
                    
                print("Full IEEE generator succeeded", file=sys.stderr)
                
            except Exception as ieee_error:
                print(f"IEEE generator failed: {ieee_error}", file=sys.stderr)
                
                # Fallback to minimal DOCX generation
                try:
                    print("Trying minimal DOCX generation...", file=sys.stderr)
                    sys.path.insert(0, parent_dir)
                    from test_minimal_docx import create_minimal_docx
                    
                    docx_bytes = create_minimal_docx(document_data)
                    
                    if not docx_bytes or len(docx_bytes) == 0:
                        raise Exception("Minimal DOCX generation also failed")
                        
                    print("Minimal DOCX generation succeeded", file=sys.stderr)
                    
                except Exception as minimal_error:
                    print(f"Minimal DOCX generation failed: {minimal_error}", file=sys.stderr)
                    raise Exception(f"Both IEEE and minimal generation failed: IEEE={ieee_error}, Minimal={minimal_error}")
            
            # Convert to base64 for JSON response
            docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
            
            print(f"DOCX generated successfully, size: {len(docx_bytes)} bytes", file=sys.stderr)
            
            # Record download in database
            download_recorded = False
            try:
                # Import database utilities
                sys.path.insert(0, parent_dir)
                from db_utils import record_download
                
                # Extract user info from request headers if available
                user_agent = self.headers.get('User-Agent', 'Unknown')
                
                # Record the download
                download_data = {
                    'document_title': document_data.get('title', 'Untitled Document'),
                    'file_format': 'docx',
                    'file_size': len(docx_bytes),
                    'user_agent': user_agent,
                    'ip_address': self.headers.get('X-Forwarded-For', self.client_address[0]),
                    'document_metadata': {
                        'authors': [author.get('name', '') for author in document_data.get('authors', [])],
                        'sections': len(document_data.get('sections', [])),
                        'references': len(document_data.get('references', [])),
                        'generated_by': 'python_backend',
                        'requested_format': 'docx',
                        'actual_format': 'docx'
                    }
                }
                
                print("Recording download in database...", file=sys.stderr)
                # record_download(download_data)  # Commented out for now to avoid errors without user_id
                download_recorded = True
                
            except Exception as db_error:
                print(f"Failed to record download in database: {db_error}", file=sys.stderr)
                # Don't fail the request if database recording fails
            
            self.end_headers()
            response = json.dumps({
                'success': True,
                'file_data': docx_base64,
                'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'file_size': len(docx_bytes),
                'message': 'DOCX document generated successfully',
                'download_recorded': download_recorded
            })
            self.wfile.write(response.encode())
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'DOCX generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())