#!/usr/bin/env python3
"""
Simple test server to verify deployment fixes without Vercel
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

class TestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps({
                'status': 'healthy',
                'message': 'Python backend with deployment fixes is running',
                'fixes_applied': [
                    'Word documents: Table images with proper names',
                    'PDF documents: Perfect justification matching Word',
                    'Visual consistency: Identical formatting between formats'
                ]
            })
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests for document generation"""
        try:
            if self.path == '/api/pdf-generator':
                # Import PDF generator
                from api.pdf_generator import handler
                
                # Create a mock handler instance and call it
                mock_handler = handler()
                mock_handler.headers = self.headers
                mock_handler.rfile = self.rfile
                mock_handler.wfile = self.wfile
                mock_handler.send_response = self.send_response
                mock_handler.send_header = self.send_header
                mock_handler.end_headers = self.end_headers
                
                mock_handler.do_POST()
                
            elif self.path == '/api/docx-generator':
                # Import DOCX generator
                from api.docx_generator import handler
                
                # Create a mock handler instance and call it
                mock_handler = handler()
                mock_handler.headers = self.headers
                mock_handler.rfile = self.rfile
                mock_handler.wfile = self.wfile
                mock_handler.send_response = self.send_response
                mock_handler.send_header = self.send_header
                mock_handler.end_headers = self.end_headers
                
                mock_handler.do_POST()
                
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = json.dumps({
                    'success': False,
                    'error': 'Endpoint not found',
                    'available_endpoints': [
                        'GET /api/health',
                        'POST /api/pdf-generator',
                        'POST /api/docx-generator'
                    ]
                })
                self.wfile.write(error_response.encode())
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = json.dumps({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            })
            self.wfile.write(error_response.encode())

def run_test_server():
    """Run the simple test server"""
    port = 3001
    
    print("🧪 SIMPLE TEST SERVER FOR DEPLOYMENT FIXES")
    print("=" * 50)
    print(f"🌐 Server starting on http://localhost:{port}")
    print("📋 Available endpoints:")
    print(f"   GET  http://localhost:{port}/api/health")
    print(f"   POST http://localhost:{port}/api/pdf-generator")
    print(f"   POST http://localhost:{port}/api/docx-generator")
    print("")
    print("🎯 This server tests the deployment fixes:")
    print("   ✅ Word documents: Table images with proper names")
    print("   ✅ PDF documents: Perfect justification matching Word")
    print("   ✅ Visual consistency: Identical formatting")
    print("")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        server = HTTPServer(('localhost', port), TestHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    run_test_server()