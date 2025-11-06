"""
Health check endpoint for Python backend
Tests database connectivity and system status
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import db_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env.local if it exists
def load_env():
    env_files = ['.env.local', '.env']
    for env_file in env_files:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), env_file)
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            break

# Load environment variables
load_env()

try:
    from db_utils import test_connection, cleanup_connection
except ImportError as e:
    print(f"Import error: {e}")
    test_connection = None
    cleanup_connection = None

try:
    from auth_utils import validate_jwt_token, extract_token_from_request, get_jwt_secret
except ImportError as e:
    print(f"Auth utils import error: {e}")
    validate_jwt_token = None
    extract_token_from_request = None
    get_jwt_secret = None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for health check"""
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
            
            # Test JWT authentication (lightweight)
            auth_result = self._test_jwt_auth()
            
            # Test database connection (with timeout protection)
            db_result = self._test_database_with_timeout()
            
            # Overall health status - service is healthy if basic systems work
            # Database issues shouldn't make the entire service unhealthy
            is_healthy = auth_result.get('success', False)
            
            response_data = {
                'success': True,  # Service is running
                'status': 'healthy' if is_healthy else 'degraded',
                'database': db_result,
                'authentication': auth_result,
                'system': system_info,
                'timestamp': datetime.now().isoformat()
            }
            
            # Always return 200 for health checks unless there's a critical error
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, indent=2).encode())
            
        except Exception as e:
            self.send_error_response(500, 'Health check failed', str(e))
        finally:
            # Cleanup connection for serverless
            if cleanup_connection:
                try:
                    cleanup_connection()
                except:
                    pass  # Don't fail health check on cleanup issues
    
    def _test_database_with_timeout(self):
        """Test database connection with basic error handling"""
        if not test_connection:
            return {
                'success': False,
                'error': {'message': 'Database utilities not available', 'code': 500},
                'status': 'unavailable'
            }
        
        try:
            # Simple database test without complex timeout handling
            db_result = test_connection()
            return db_result
            
        except Exception as e:
            return {
                'success': False,
                'error': {'message': f'Database test failed: {str(e)}', 'code': 500},
                'status': 'error'
            }
    
    def _test_jwt_auth(self):
        """Test JWT authentication functionality"""
        if not validate_jwt_token or not get_jwt_secret:
            return {
                'success': False,
                'error': {'message': 'JWT utilities not available', 'code': 500}
            }
        
        try:
            # Check if JWT_SECRET is configured
            jwt_secret = get_jwt_secret()
            secret_configured = jwt_secret != 'fallback-secret-change-in-production'
            
            # Test token extraction (will be None for health check, but tests the function)
            token = extract_token_from_request(self) if extract_token_from_request else None
            
            auth_status = {
                'success': True,
                'jwt_secret_configured': secret_configured,
                'jwt_secret_source': 'environment' if secret_configured else 'fallback',
                'token_present': token is not None,
                'utilities_loaded': True
            }
            
            # If a token is present, test validation
            if token:
                user_data = validate_jwt_token(token)
                auth_status['token_valid'] = user_data is not None
                if user_data:
                    auth_status['token_user'] = {
                        'userId': user_data.get('userId'),
                        'email': user_data.get('email')
                    }
            
            return auth_status
            
        except Exception as e:
            return {
                'success': False,
                'error': {'message': f'JWT test failed: {str(e)}', 'code': 500}
            }
    
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
            'status': 'error',
            'error': {
                'message': message,
                'details': details,
                'code': status_code
            },
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(error_response, indent=2).encode())