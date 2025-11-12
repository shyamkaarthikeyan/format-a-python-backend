"""
Diagnostic endpoint to check Python backend status
"""

import json
import sys
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Diagnostic information"""
        try:
            # Basic system info
            diagnostic_info = {
                'status': 'running',
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'environment_vars': {
                    'VERCEL_ENV': os.environ.get('VERCEL_ENV', 'not_set'),
                    'NODE_ENV': os.environ.get('NODE_ENV', 'not_set'),
                    'ALLOWED_ORIGINS': os.environ.get('ALLOWED_ORIGINS', 'not_set')
                },
                'sys_path': sys.path[:5],  # First 5 entries
                'available_files': []
            }
            
            # Check for key files
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.join(current_dir, '..')
                
                key_files = [
                    'ieee_generator_fixed.py',
                    'cors_utils.py',
                    'docx_to_pdf_converter.py',
                    'requirements.txt'
                ]
                
                for filename in key_files:
                    filepath = os.path.join(parent_dir, filename)
                    diagnostic_info['available_files'].append({
                        'file': filename,
                        'exists': os.path.exists(filepath),
                        'path': filepath
                    })
                    
            except Exception as e:
                diagnostic_info['file_check_error'] = str(e)
            
            # Test imports
            diagnostic_info['imports'] = {}
            
            try:
                sys.path.insert(0, parent_dir)
                from ieee_generator_fixed import generate_ieee_document
                diagnostic_info['imports']['ieee_generator_fixed'] = 'success'
            except Exception as e:
                diagnostic_info['imports']['ieee_generator_fixed'] = f'failed: {str(e)}'
            
            try:
                from cors_utils import handle_preflight
                diagnostic_info['imports']['cors_utils'] = 'success'
            except Exception as e:
                diagnostic_info['imports']['cors_utils'] = f'failed: {str(e)}'
            
            try:
                from docx_to_pdf_converter import convert_docx_to_pdf
                diagnostic_info['imports']['docx_to_pdf_converter'] = 'success'
            except Exception as e:
                diagnostic_info['imports']['docx_to_pdf_converter'] = f'failed: {str(e)}'
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(diagnostic_info, indent=2).encode('utf-8'))
            
        except Exception as e:
            # Emergency response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_info = {
                'status': 'error',
                'error': str(e),
                'python_version': sys.version
            }
            
            self.wfile.write(json.dumps(error_info).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()