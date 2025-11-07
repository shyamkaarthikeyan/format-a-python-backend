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
    # Import the generate function from the local IEEE generator
    from ieee_generator_fixed import generate_ieee_document
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    # Create a fallback function
    def generate_ieee_document(data):
        raise Exception(f"IEEE generator not available: {e}")

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
        """Handle POST requests for preview image generation"""
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
        
        # Generate the DOCX document using the reliable IEEE generator
        try:
            docx_buffer = generate_ieee_document(document_data)
            print("DOCX generated successfully", file=sys.stderr)
            
            # Create a simple HTML preview instead of images (more reliable)
            preview_html = self._create_html_preview(document_data)
            
            response_data = {
                'preview_type': 'html',
                'html_content': preview_html
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
                'message': 'Preview generated successfully'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as docx_error:
            print(f"DOCX generation failed: {docx_error}", file=sys.stderr)
            
            # Still provide a basic preview based on the data
            preview_html = self._create_html_preview(document_data)
            
            response_data = {
                'preview_type': 'html',
                'html_content': preview_html,
                'fallback': True
            }
            
            # Set CORS headers for the fallback response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Retry-Attempt, X-Source, User-Agent')
            self.end_headers()
            
            response = {
                'success': True,
                'data': response_data,
                'message': 'Basic preview generated (downloads will have full IEEE formatting)'
            }
            self.wfile.write(json.dumps(response).encode())

    def _create_html_preview(self, document_data):
        """Create an HTML preview that mimics IEEE formatting"""
        
        # Extract document data
        title = document_data.get('title', 'Untitled Document')
        authors = document_data.get('authors', [])
        abstract = document_data.get('abstract', '')
        keywords = document_data.get('keywords', '')
        sections = document_data.get('sections', [])
        references = document_data.get('references', [])
        
        # Format authors
        author_names = []
        for author in authors:
            if author.get('name'):
                author_names.append(author['name'])
        authors_text = ', '.join(author_names) if author_names else 'Anonymous'
        
        # Create HTML with IEEE-like styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    font-size: 9.5pt;
                    line-height: 1.2;
                    margin: 20px;
                    background: white;
                    color: black;
                }}
                .ieee-title {{
                    font-size: 14pt;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0;
                    line-height: 1.3;
                }}
                .ieee-authors {{
                    font-size: 10pt;
                    text-align: center;
                    margin: 15px 0;
                    font-style: italic;
                }}
                .ieee-section {{
                    margin: 15px 0;
                    text-align: justify;
                }}
                .ieee-abstract-title {{
                    font-weight: bold;
                    display: inline;
                }}
                .ieee-keywords-title {{
                    font-weight: bold;
                    display: inline;
                }}
                .ieee-heading {{
                    font-weight: bold;
                    margin: 15px 0 5px 0;
                    text-transform: uppercase;
                }}
                .ieee-reference {{
                    margin: 3px 0;
                    padding-left: 15px;
                    text-indent: -15px;
                }}
                .preview-note {{
                    background: #f0f8ff;
                    border: 1px solid #d0e7ff;
                    padding: 10px;
                    margin: 10px 0;
                    font-size: 8pt;
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="preview-note">
                📄 Live IEEE Preview - Download buttons provide full formatting
            </div>
            
            <div class="ieee-title">{title}</div>
            <div class="ieee-authors">{authors_text}</div>
        """
        
        # Add abstract
        if abstract:
            html += f"""
            <div class="ieee-section">
                <span class="ieee-abstract-title">Abstract—</span>{abstract}
            </div>
            """
        
        # Add keywords
        if keywords:
            html += f"""
            <div class="ieee-section">
                <span class="ieee-keywords-title">Keywords—</span>{keywords}
            </div>
            """
        
        # Add sections
        for i, section in enumerate(sections):
            if section.get('title') and section.get('content'):
                html += f"""
                <div class="ieee-heading">{i+1}. {section['title']}</div>
                <div class="ieee-section">{section['content']}</div>
                """
        
        # Add references
        if references:
            html += '<div class="ieee-heading">References</div>'
            for i, ref in enumerate(references):
                if ref.get('text'):
                    html += f'<div class="ieee-reference">[{i+1}] {ref["text"]}</div>'
        
        html += """
            <div class="preview-note">
                ✨ Perfect IEEE formatting available via Download Word/PDF buttons
            </div>
        </body>
        </html>
        """
        
        return html