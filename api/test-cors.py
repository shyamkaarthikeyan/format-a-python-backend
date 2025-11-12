"""
Minimal CORS test endpoint to verify Python backend is working
"""

import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests - minimal version"""
        print("🌐 CORS preflight request received", flush=True)
        
        # Send response
        self.send_response(200)
        
        # Set CORS headers
        self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        
        # End headers
        self.end_headers()
        
        print("✅ CORS preflight response sent", flush=True)

    def do_GET(self):
        """Handle GET requests"""
        print("📡 GET request received", flush=True)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
        self.end_headers()
        
        response = {
            'success': True,
            'message': 'Python backend is working!',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print("✅ GET response sent", flush=True)

    def do_POST(self):
        """Handle POST requests"""
        print("📡 POST request received", flush=True)
        
        try:
            # Read request data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            response = {
                'success': True,
                'message': 'POST request successful!',
                'received_bytes': len(post_data),
                'timestamp': '2024-01-01T00:00:00Z'
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            print("✅ POST response sent", flush=True)
            
        except Exception as e:
            print(f"❌ POST error: {e}", flush=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))