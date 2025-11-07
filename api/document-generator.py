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
    # Import both DOCX and HTML preview functions from the IEEE generator
    from ieee_generator_fixed import generate_ieee_document, generate_ieee_html_preview
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    # Create fallback functions
    def generate_ieee_document(data):
        raise Exception(f"IEEE generator not available: {e}")
    def generate_ieee_html_preview(data):
        raise Exception(f"IEEE HTML preview generator not available: {e}")

# Import error handling utilities
try:
    from error_utils import (
        with_error_handling, send_success_response, send_error_response,
        validate_request_data, APIError, ErrorTypes, health_monitor, log_performance
    )
except ImportError as e:
    print(f"Error utils import failed: {e}", file=sys.stderr)
    # Fallback decorator
    def with_error_handling(func):
        return func
    def log_performance(name):
        def decorator(func):
            return func
        return decorator

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Retry-Attempt, X-Source, User-Agent')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

    @with_error_handling
    @log_performance("document_preview_generation")
    def do_POST(self):
        """Handle POST requests for preview generation using ieee_generator_fixed.py ONLY"""
        # Record request for monitoring
        if 'health_monitor' in globals():
            health_monitor.record_request()
        
        # Read and validate request body
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            raise APIError(
                message="Empty request body",
                error_type=ErrorTypes.VALIDATION_ERROR,
                status_code=400
            )
            
        post_data = self.rfile.read(content_length)
        document_data = json.loads(post_data.decode('utf-8'))
        
        # Validate required fields
        validate_request_data(document_data, ['title'])
        
        # Generate HTML preview using ieee_generator_fixed.py
        try:
            print("Generating HTML preview using ieee_generator_fixed.py", file=sys.stderr)
            preview_html = generate_ieee_html_preview(document_data)
            
            # Also verify DOCX generation works
            try:
                docx_buffer = generate_ieee_document(document_data)
                print("DOCX generation verified successfully", file=sys.stderr)
            except Exception as docx_error:
                print(f"DOCX generation failed: {docx_error}", file=sys.stderr)
            
            response_data = {
                'preview_type': 'html',
                'html_content': preview_html,
                'generator': 'ieee_generator_fixed.py'
            }
            
            # Set CORS headers for the response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Retry-Attempt, X-Source, User-Agent')
            self.end_headers()
            
            response = {
                'success': True,
                'data': response_data,
                'message': 'IEEE preview generated successfully using ieee_generator_fixed.py'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as preview_error:
            print(f"IEEE preview generation failed: {preview_error}", file=sys.stderr)
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Retry-Attempt, X-Source, User-Agent')
            self.end_headers()
            
            response = {
                'success': False,
                'error': 'Preview generation failed',
                'message': f'IEEE preview generation failed: {str(preview_error)}',
                'generator': 'ieee_generator_fixed.py'
            }
            self.wfile.write(json.dumps(response).encode())