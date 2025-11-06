"""
Simple health check endpoint for Python backend
Basic functionality test without database dependencies
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for simple health check"""
        try:
            # System information (always available)
            system_info = {
                'python_version': sys.version,
                'environment': os.environ.get('VERCEL_ENV', 'development'),
                'timestamp': datetime.now().isoformat(),
                'database_url_configured': bool(os.environ.get('DATABASE_URL')),
                'jwt_secret_configured': bool(os.environ.get('JWT_SECRET')),
                'service': 'format-a-python-backend',
                'status': 'running'
            }
            
            # Environment variables check
            env_check = {
                'DATABASE_URL': 'configured' if os.environ.get('DATABASE_URL') else 'missing',
                'JWT_SECRET': 'configured' if os.environ.get('JWT_SECRET') else 'missing',
                'VITE_GOOGLE_CLIENT_ID': 'configured' if os.environ.get('VITE_GOOGLE_CLIENT_ID') else 'missing',
                'EMAIL_USER': 'configured' if os.environ.get('EMAIL_USER') else 'missing',
                'EMAIL_PASS': 'configured' if os.environ.get('EMAIL_PASS') else 'missing'
            }
            
            # Check if all required environment variables are present
            required_vars = ['DATABASE_URL', 'JWT_SECRET', 'VITE_GOOGLE_CLIENT_ID']
            missing_vars = [var for var in required_vars if not os.environ.get(var)]
            
            is_healthy = len(missing_vars) == 0
            
            response_data = {
                'success': True,
                'status': 'healthy' if is_healthy else 'degraded',
                'message': 'Python backend is running' if is_healthy else f'Missing environment variables: {missing_vars}',
                'environment_variables': env_check,
                'system': system_info,
                'missing_variables': missing_vars,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            self.send_error_response(500, 'Health check failed', str(e))
    
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