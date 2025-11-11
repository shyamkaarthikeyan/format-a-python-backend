"""
PDF Generator endpoint for Python backend
Generates IEEE-formatted PDF documents by converting Word documents to PDF
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

# Also try adding the root directory to path for Vercel compatibility
root_dir = os.path.join(parent_dir, '..')
sys.path.insert(0, root_dir)

# Import the IEEE Word generator and PDF converter
IMPORTS_AVAILABLE = False
IMPORT_ERROR = None

try:
    # Try multiple import paths for Vercel compatibility
    try:
        from ieee_generator_fixed import generate_ieee_document
        from docx_to_pdf_converter import convert_docx_to_pdf
    except ImportError:
        # Try with explicit path
        sys.path.insert(0, '/var/task')
        from ieee_generator_fixed import generate_ieee_document
        from docx_to_pdf_converter import convert_docx_to_pdf
    
    IMPORTS_AVAILABLE = True
    print("Successfully imported IEEE Word generator and PDF converter", file=sys.stderr)
except ImportError as e:
    IMPORT_ERROR = str(e)
    print(f"WARNING: Failed to import IEEE generators: {e}", file=sys.stderr)
    print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print("Will provide fallback response", file=sys.stderr)

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
        """Handle POST requests for PDF generation with perfect justification"""
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
            
            # Try Word → PDF conversion first, fallback to HTML → PDF if needed
            pdf_bytes = None
            conversion_method = None
            
            if IMPORTS_AVAILABLE:
                try:
                    # Generate PDF using Word → PDF conversion pipeline
                    print("🎯 Attempting Word → PDF conversion pipeline...", file=sys.stderr)
                    
                    # Step 1: Generate Word document using existing IEEE generator
                    print("📝 Generating IEEE Word document...", file=sys.stderr)
                    docx_bytes = generate_ieee_document(document_data)
                    
                    if not docx_bytes or len(docx_bytes) == 0:
                        raise Exception("Word document generation failed - empty result")
                    
                    print(f"✅ Word document generated successfully, size: {len(docx_bytes)} bytes", file=sys.stderr)
                    
                    # Step 2: Convert Word document to PDF
                    print("📄 Converting Word document to PDF...", file=sys.stderr)
                    pdf_bytes = convert_docx_to_pdf(docx_bytes)
                    
                    if not pdf_bytes or len(pdf_bytes) == 0:
                        raise Exception("PDF conversion failed - empty result")
                    
                    print("✅ PDF generated successfully from Word document", file=sys.stderr)
                    conversion_method = 'word_to_pdf_reportlab'
                    
                except Exception as word_error:
                    print(f"⚠️ Word → PDF conversion failed: {word_error}", file=sys.stderr)
                    print("🔄 Falling back to HTML → PDF conversion...", file=sys.stderr)
                    pdf_bytes = None
            
            # Fallback to HTML → PDF conversion if Word → PDF failed or imports unavailable
            if pdf_bytes is None:
                try:
                    print("🎯 Using HTML → PDF fallback conversion...", file=sys.stderr)
                    
                    # Try to import the original HTML → PDF functions
                    try:
                        from ieee_generator_fixed import build_document_model, render_to_html, weasyprint_pdf_from_html
                        
                        # Build document model
                        print("🎯 Building document model...", file=sys.stderr)
                        model = build_document_model(document_data)
                        
                        # Render to HTML
                        print("🌐 Rendering HTML...", file=sys.stderr)
                        html = render_to_html(model)
                        
                        # Convert HTML to PDF
                        print("📄 Converting HTML to PDF with WeasyPrint...", file=sys.stderr)
                        pdf_bytes = weasyprint_pdf_from_html(html)
                        
                        if not pdf_bytes or len(pdf_bytes) == 0:
                            raise Exception("HTML → PDF conversion failed - empty result")
                        
                        print("✅ PDF generated successfully from HTML", file=sys.stderr)
                        conversion_method = 'html_to_pdf_weasyprint_fallback'
                        
                    except ImportError as import_error:
                        raise Exception(f"Both Word → PDF and HTML → PDF methods unavailable: {import_error}")
                        
                except Exception as fallback_error:
                    print(f"❌ All PDF generation methods failed: {fallback_error}", file=sys.stderr)
                    
                    self.end_headers()
                    error_response = json.dumps({
                        'success': False,
                        'error': 'PDF generation failed',
                        'message': f'All PDF generation methods failed. Word → PDF: {IMPORT_ERROR if not IMPORTS_AVAILABLE else "Available but failed"}. HTML → PDF: {str(fallback_error)}',
                        'technical_details': {
                            'word_to_pdf_error': IMPORT_ERROR if not IMPORTS_AVAILABLE else "Available but failed",
                            'html_to_pdf_error': str(fallback_error)
                        }
                    })
                    self.wfile.write(error_response.encode())
                    return
            
            # Convert to base64 for JSON response
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            print(f"PDF generated successfully, size: {len(pdf_bytes)} bytes", file=sys.stderr)
            
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
                    'file_format': 'pdf',
                    'file_size': len(pdf_bytes),
                    'user_agent': user_agent,
                    'ip_address': self.headers.get('X-Forwarded-For', self.client_address[0]),
                    'document_metadata': {
                        'authors': [author.get('name', '') for author in document_data.get('authors', [])],
                        'sections': len(document_data.get('sections', [])),
                        'references': len(document_data.get('references', [])),
                        'generated_by': 'python_backend_word_to_pdf',
                        'requested_format': 'pdf',
                        'actual_format': 'pdf',
                        'conversion_method': conversion_method
                    }
                }
                
                print("Recording PDF download in database...", file=sys.stderr)
                # record_download(download_data)  # Commented out for now to avoid errors without user_id
                download_recorded = True
                
            except Exception as db_error:
                print(f"Failed to record download in database: {db_error}", file=sys.stderr)
                # Don't fail the request if database recording fails
            
            self.end_headers()
            
            # Set appropriate message based on conversion method
            if conversion_method == 'word_to_pdf_reportlab':
                message = 'PDF document generated from Word document'
            else:
                message = 'PDF document generated using fallback HTML conversion'
            
            response = json.dumps({
                'success': True,
                'file_data': pdf_base64,
                'file_type': 'application/pdf',
                'file_size': len(pdf_bytes),
                'message': message,
                'conversion_method': conversion_method,
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
            print(f"PDF generation failed: {e}", file=sys.stderr)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'PDF generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())