"""
Simple test endpoint for Python backend
Basic functionality test without database dependencies
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        try:
            response_data = {
                'success': True,
                'message': 'Python backend is working!',
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'environment': os.environ.get('VERCEL_ENV', 'development'),
                'path': self.path
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            self.send_error_response(500, 'Test endpoint failed', str(e))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def send_error_response(self, status_code: int, message: str, details: str = None):
        """Send standardized error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': {
                'message': message,
                'details': details,
                'code': status_code
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(error_response, indent=2).encode())