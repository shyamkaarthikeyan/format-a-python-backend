import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# Add parent directory to path to import ieee_generator_fixed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)

# Import ieee_generator_fixed - no fallback
from ieee_generator_fixed import generate_ieee_document
print("✅ Successfully imported ieee_generator_fixed", file=sys.stderr)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests with better error handling"""
        origin = self.headers.get('Origin')
        print(f"🌐 CORS preflight request from origin: {origin}", file=sys.stderr)
        
        # Send successful preflight response
        self.send_response(200)
        
        # Set CORS headers
        if origin == 'https://format-a.vercel.app':
            self.send_header('Access-Control-Allow-Origin', origin)
            print("✅ CORS preflight for allowed origin", file=sys.stderr)
        else:
            # For debugging, allow the origin but log it
            print(f"⚠️ CORS preflight for unknown origin, allowing for debugging: {origin}", file=sys.stderr)
            self.send_header('Access-Control-Allow-Origin', origin or 'https://format-a.vercel.app')
        
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Source, X-Original-Path, X-Generator')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        
        print("✅ CORS preflight handled successfully", file=sys.stderr)

    def do_POST(self):
        """Generate IEEE document - direct conversion only, no fallbacks"""
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            document_data = json.loads(post_data.decode('utf-8'))
            
            # Debug logging
            format_value = document_data.get('format')
            action_value = document_data.get('action')
            print(f"🔍 Request format: '{format_value}', action: '{action_value}'", file=sys.stderr)
            
            # Check if this is a DOCX→PDF conversion request (no title validation needed)
            if document_data.get('format') == 'docx-to-pdf':
                print("📄 Handling DOCX→PDF conversion request", file=sys.stderr)
                self.handle_docx_to_pdf_conversion(document_data)
                return
            
            # Validate required field for document generation
            if not document_data.get('title'):
                self.send_error_response(400, 'Title is required')
                return
            
            # Check if this is a PDF request (generate DOCX then convert to PDF)
            if document_data.get('format') == 'pdf':
                print("🎯 Handling PDF generation request via DOCX→PDF conversion", file=sys.stderr)
                self.handle_pdf_via_docx_conversion(document_data)
                return
            
            # Check if this is a DOCX download request
            if document_data.get('format') == 'docx' and document_data.get('action') == 'download':
                print("📄 Handling DOCX download request", file=sys.stderr)
                self.handle_docx_download(document_data)
                return
            
            # Generate preview using DOCX→PDF conversion (consistent formatting)
            print("🌐 Generating preview using DOCX→PDF conversion for consistent formatting...", file=sys.stderr)
            
            # Step 1: Generate DOCX document
            print("📄 Step 1: Generating DOCX document for preview...", file=sys.stderr)
            docx_bytes = generate_ieee_document(document_data)
            
            if not docx_bytes or len(docx_bytes) == 0:
                raise Exception("DOCX generation failed for preview")
            
            print(f"✅ DOCX generated for preview (size: {len(docx_bytes)} bytes)", file=sys.stderr)
            
            # Step 2: Convert DOCX to PDF using PDFKit
            print("📄 Step 2: Converting DOCX to PDF for preview...", file=sys.stderr)
            
            # Import the PDFKit-based DOCX to PDF converter
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from docx_to_pdf_converter import convert_docx_to_pdf_direct
            
            # Convert DOCX to PDF
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise Exception("DOCX→PDF conversion failed for preview")
            
            print(f"✅ PDF preview generated via DOCX→PDF conversion (size: {len(pdf_bytes)} bytes)", file=sys.stderr)
            
            # Convert to base64 for response
            import base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Send success response with PDF data
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                'success': True,
                'file_data': pdf_base64,
                'file_type': 'application/pdf',
                'file_size': len(pdf_bytes),
                'message': 'PDF preview generated successfully via DOCX→PDF conversion',
                'conversion_method': 'docx_to_pdf_conversion',
                'generator': 'ieee_generator_fixed.py'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            self.send_error_response(500, f'Document generation failed: {str(e)}')
    
    def handle_pdf_via_docx_conversion(self, document_data):
        """Handle PDF generation requests - Generate DOCX first, then convert to PDF"""
        try:
            import base64
            
            print("🎯 Starting PDF generation via DOCX→PDF conversion...", file=sys.stderr)
            
            # Step 1: Generate DOCX document
            print("📄 Step 1: Generating DOCX document...", file=sys.stderr)
            docx_bytes = generate_ieee_document(document_data)
            
            if not docx_bytes or len(docx_bytes) == 0:
                raise Exception("DOCX generation failed - empty result")
            
            print(f"✅ DOCX generated (size: {len(docx_bytes)} bytes)", file=sys.stderr)
            
            # Step 2: Convert DOCX to PDF using PDFKit
            print("📄 Step 2: Converting DOCX to PDF using PDFKit...", file=sys.stderr)
            
            # Import the PDFKit-based DOCX to PDF converter
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from docx_to_pdf_converter import convert_docx_to_pdf_direct
            
            # Convert DOCX to PDF
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise Exception("DOCX→PDF conversion failed - empty result")
            
            print(f"✅ PDF generated via DOCX→PDF conversion (size: {len(pdf_bytes)} bytes)", file=sys.stderr)
            
            # Convert to base64 for JSON response
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Send success response with strict CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                'success': True,
                'file_data': pdf_base64,
                'file_type': 'application/pdf',
                'file_size': len(pdf_bytes),
                'message': 'PDF generated successfully via DOCX→PDF conversion',
                'conversion_method': 'docx_to_pdf_conversion',
                'requested_format': 'pdf',
                'actual_format': 'pdf'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ PDF generation via DOCX→PDF conversion failed: {e}", file=sys.stderr)
            self.send_error_response(500, f'PDF generation via DOCX→PDF conversion failed: {str(e)}')

    def handle_docx_to_pdf_conversion(self, request_data):
        """Handle DOCX to PDF conversion requests - Direct Word→PDF conversion ONLY"""
        try:
            import base64
            
            # Import the PDFKit-based DOCX to PDF converter
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from docx_to_pdf_converter import convert_docx_to_pdf_direct
            
            print("🎯 Starting direct Word→PDF conversion...", file=sys.stderr)
            
            # Get DOCX data from request
            docx_data_b64 = request_data.get('docx_data')
            if not docx_data_b64:
                raise Exception("No DOCX data provided for conversion")
            
            # Decode base64 DOCX data
            docx_bytes = base64.b64decode(docx_data_b64)
            
            if not docx_bytes or len(docx_bytes) == 0:
                raise Exception("Invalid DOCX data for conversion")
            
            print(f"📄 Direct Word→PDF conversion (input size: {len(docx_bytes)} bytes)...", file=sys.stderr)
            
            # Convert DOCX to PDF using direct conversion (preserves all Word formatting)
            pdf_bytes = convert_docx_to_pdf_direct(docx_bytes)
            
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise Exception("Direct Word→PDF conversion failed - empty result")
            
            print(f"✅ Direct Word→PDF conversion successful, output size: {len(pdf_bytes)} bytes", file=sys.stderr)
            
            # Convert to base64 for JSON response
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Send success response with strict CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                'success': True,
                'file_data': pdf_base64,
                'file_type': 'application/pdf',
                'file_size': len(pdf_bytes),
                'message': 'PDF generated successfully via direct Word→PDF conversion',
                'conversion_method': 'direct_docx2pdf',
                'requested_format': 'pdf',
                'actual_format': 'pdf'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Direct Word→PDF conversion failed: {e}", file=sys.stderr)
            self.send_error_response(500, f'Direct Word→PDF conversion failed: {str(e)}')

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
            
            # Send success response with strict CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
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
    
    def send_cors_headers(self):
        """Send CORS headers with better error handling"""
        origin = self.headers.get('Origin')
        print(f"🌐 Sending CORS headers for origin: {origin}", file=sys.stderr)
        
        # Allow the frontend domain
        if origin == 'https://format-a.vercel.app':
            self.send_header('Access-Control-Allow-Origin', origin)
            print("✅ CORS headers sent for allowed origin", file=sys.stderr)
        else:
            # For debugging, allow the origin but log it
            print(f"⚠️ Unknown origin, but allowing for debugging: {origin}", file=sys.stderr)
            self.send_header('Access-Control-Allow-Origin', origin or 'https://format-a.vercel.app')
    
    def send_error_response(self, status_code, error_message):
        """Send error response with strict CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'success': False,
            'error': error_message,
            'generator': 'ieee_generator_fixed.py'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))