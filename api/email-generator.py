"""
Email Generator endpoint for Python backend
Generates and sends IEEE-formatted documents via email
"""

import json
import sys
import os
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
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
        """Handle POST requests for email generation and sending"""
        try:
            # Read request body FIRST (before sending any response)
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Empty request body',
                    'message': 'Email data is required'
                })
                self.wfile.write(error_response.encode())
                return
                
            post_data = self.rfile.read(content_length)
            email_data = json.loads(post_data.decode('utf-8'))
            
            # Extract email and document data
            recipient_email = email_data.get('email')
            document_data = email_data.get('documentData')
            file_data_base64 = email_data.get('fileData')  # Pre-generated file (base64)
            
            # Validate required fields
            if not recipient_email:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
                self.end_headers()
                error_response = json.dumps({
                    'success': False,
                    'error': 'Missing email address',
                    'message': 'Recipient email address is required'
                })
                self.wfile.write(error_response.encode())
                return
            
            # Check if we have pre-generated file data
            if file_data_base64:
                # Use the already-generated file (same as downloaded)
                print(f"Using pre-generated document for email to {recipient_email}...", file=sys.stderr)
                print(f"   File data length: {len(file_data_base64)} characters", file=sys.stderr)
                
                # Decode base64 to bytes
                import base64
                try:
                    docx_bytes = base64.b64decode(file_data_base64)
                    docx_buffer = BytesIO(docx_bytes)
                    print(f"   Decoded to {len(docx_bytes)} bytes", file=sys.stderr)
                except Exception as decode_error:
                    print(f"   ❌ Failed to decode base64: {decode_error}", file=sys.stderr)
                    raise Exception(f"Invalid base64 file data: {decode_error}")
                
                document_title = document_data.get('title', 'IEEE Paper') if document_data else 'IEEE Paper'
                print(f"   Document title: {document_title}", file=sys.stderr)
                
            else:
                # Generate fresh document (fallback)
                if not document_data:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
                    self.end_headers()
                    error_response = json.dumps({
                        'success': False,
                        'error': 'Missing document data',
                        'message': 'Document data or file data is required'
                    })
                    self.wfile.write(error_response.encode())
                    return
                
                if not document_data.get('title'):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
                    self.end_headers()
                    error_response = json.dumps({
                        'success': False,
                        'error': 'Missing document title',
                        'message': 'Document title is required'
                    })
                    self.wfile.write(error_response.encode())
                    return
                
                print(f"Generating fresh document for email to {recipient_email}...", file=sys.stderr)
                docx_result = generate_ieee_document(document_data)
                
                # Handle both bytes and BytesIO objects
                if isinstance(docx_result, bytes):
                    docx_buffer = BytesIO(docx_result)
                else:
                    docx_buffer = docx_result
                
                document_title = document_data.get('title', 'IEEE Paper')
            
            # Validate docx_buffer
            if not docx_buffer:
                raise Exception("Document buffer is None")
            
            if not isinstance(docx_buffer, BytesIO):
                raise Exception(f"Document buffer is wrong type: {type(docx_buffer).__name__}, expected BytesIO")
            
            try:
                buffer_content = docx_buffer.getvalue()
                if buffer_content == b'':
                    raise Exception("Document is empty")
                print(f"   Document buffer size: {len(buffer_content)} bytes", file=sys.stderr)
            except AttributeError as e:
                raise Exception(f"Document buffer has no getvalue() method. Type: {type(docx_buffer).__name__}")
            
            # Send email
            print(f"📧 Calling _send_email with:", file=sys.stderr)
            print(f"   recipient: {recipient_email}", file=sys.stderr)
            print(f"   title: {document_title}", file=sys.stderr)
            print(f"   document_data type: {type(document_data).__name__}", file=sys.stderr)
            
            email_result = self._send_email(
                recipient_email=recipient_email,
                document_title=document_title,
                document_buffer=docx_buffer,
                document_data=document_data if isinstance(document_data, dict) else {}
            )
            
            if email_result['success']:
                print(f"Email sent successfully to {recipient_email}", file=sys.stderr)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
                self.end_headers()
                response = json.dumps({
                    'success': True,
                    'message': f'IEEE paper sent successfully to {recipient_email}',
                    'email': recipient_email,
                    'document_title': document_data.get('title') if isinstance(document_data, dict) else document_title,
                    'file_size': len(docx_buffer.getvalue())
                })
                self.wfile.write(response.encode())
            else:
                raise Exception(email_result['error'])
            
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
            print(f"Email generation failed: {e}", file=sys.stderr)
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'Email generation failed',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())

    def _send_email(self, recipient_email, document_title, document_buffer, document_data):
        """Send email with document attachment using port 587 (STARTTLS)"""
        try:
            # Validate document_data type
            if not isinstance(document_data, dict):
                print(f"⚠️ document_data is not a dict, it's {type(document_data).__name__}", file=sys.stderr)
                document_data = {}  # Use empty dict as fallback
            
            # Get email configuration from environment - REQUIRED
            smtp_user = os.environ.get('EMAIL_USER')
            smtp_pass = os.environ.get('EMAIL_PASS')
            
            print(f"📧 Email config check:", file=sys.stderr)
            print(f"   EMAIL_USER: {'SET' if smtp_user else 'NOT SET'}", file=sys.stderr)
            print(f"   EMAIL_PASS: {'SET' if smtp_pass else 'NOT SET'}", file=sys.stderr)
            
            if not smtp_user or not smtp_pass:
                error_msg = 'EMAIL_USER and EMAIL_PASS must be set in Vercel environment variables'
                print(f"❌ {error_msg}", file=sys.stderr)
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = f'IEEE Paper: {document_title}'
            
            # Email body
            authors = document_data.get('authors', [])
            author_names = [author.get('name', '') for author in authors if author.get('name')]
            authors_text = ', '.join(author_names) if author_names else 'Unknown'
            
            body = f"""
Dear Recipient,

Please find attached your IEEE-formatted paper: "{document_title}"

Authors: {authors_text}

This document has been generated using the Format-A IEEE Paper Generator and follows standard IEEE formatting guidelines.

Best regards,
Format-A Team
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach document
            document_buffer.seek(0)
            attachment = MIMEApplication(document_buffer.read(), _subtype='vnd.openxmlformats-officedocument.wordprocessingml.document')
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{document_title}.docx')
            msg.attach(attachment)
            
            # Send email using port 587 with STARTTLS
            print(f"📧 Connecting to smtp.gmail.com:587...", file=sys.stderr)
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            
            print(f"📧 Starting TLS...", file=sys.stderr)
            server.starttls()
            
            print(f"📧 Logging in as {smtp_user}...", file=sys.stderr)
            server.login(smtp_user, smtp_pass)
            
            print(f"📧 Sending email to {recipient_email}...", file=sys.stderr)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent successfully to {recipient_email}", file=sys.stderr)
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            print(f"   Check EMAIL_USER and EMAIL_PASS are correct", file=sys.stderr)
            return {
                'success': False,
                'error': error_msg
            }
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            print(f"   Error type: {type(e).__name__}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                'success': False,
                'error': error_msg
            }