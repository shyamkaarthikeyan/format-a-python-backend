"""
Authentication utilities for Python backend
Provides JWT token validation matching the Node.js auth system
"""

import jwt
import os
import json
from typing import Optional, Dict, Any
from functools import wraps


def get_jwt_secret() -> str:
    """Get JWT secret from environment variables"""
    return os.environ.get('JWT_SECRET', 'fallback-secret-change-in-production')


def validate_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate JWT token using the same secret as Node.js functions
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        # Handle None or empty token
        if not token:
            return None
            
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
            
        jwt_secret = get_jwt_secret()
        decoded = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        
        # Validate required fields
        required_fields = ['userId', 'email', 'name']
        for field in required_fields:
            if field not in decoded:
                print(f"Missing required field in token: {field}")
                return None
                
        return decoded
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return None


def extract_token_from_request(handler_instance) -> Optional[str]:
    """
    Extract JWT token from HTTP request headers
    
    Args:
        handler_instance: BaseHTTPRequestHandler instance
        
    Returns:
        Token string if found, None otherwise
    """
    # Check Authorization header
    auth_header = handler_instance.headers.get('Authorization')
    if auth_header:
        return auth_header
        
    # Check for token in cookies (fallback)
    cookie_header = handler_instance.headers.get('Cookie')
    if cookie_header:
        # Simple cookie parsing for sessionId
        for cookie in cookie_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('sessionId='):
                return cookie.split('=', 1)[1]
                
    return None


def require_auth(func):
    """
    Decorator to require authentication for Python serverless functions
    
    Usage:
        @require_auth
        def do_POST(self):
            # Access authenticated user via self.current_user
            user_id = self.current_user['userId']
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Extract token from request
        token = extract_token_from_request(self)
        
        if not token:
            self.send_error_response(401, "Authentication required", "No token provided")
            return
            
        # Validate token
        user_data = validate_jwt_token(token)
        
        if not user_data:
            self.send_error_response(401, "Invalid authentication", "Token validation failed")
            return
            
        # Attach user data to handler instance
        self.current_user = user_data
        
        # Call the original function
        return func(self, *args, **kwargs)
        
    return wrapper


def send_cors_headers(handler_instance):
    """Send CORS headers for cross-origin requests"""
    handler_instance.send_header('Access-Control-Allow-Origin', 'https://format-a.vercel.app')
    handler_instance.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler_instance.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler_instance.send_header('Access-Control-Allow-Credentials', 'true')


class AuthenticatedHandler:
    """
    Mixin class to add authentication and CORS support to HTTP handlers
    """
    
    def send_error_response(self, status_code: int, message: str, details: str = None):
        """Send standardized error response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        send_cors_headers(self)
        self.end_headers()
        
        error_response = {
            'success': False,
            'error': {
                'message': message,
                'details': details,
                'code': status_code
            },
            'timestamp': self._get_timestamp()
        }
        
        self.wfile.write(json.dumps(error_response).encode())
    
    def send_success_response(self, data: Any = None, message: str = None):
        """Send standardized success response with CORS headers"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        send_cors_headers(self)
        self.end_headers()
        
        response = {
            'success': True,
            'data': data,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        send_cors_headers(self)
        self.end_headers()
    
    def _get_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def test_jwt_validation():
    """Test function to validate JWT functionality"""
    # This would be called with a real token from the Node.js auth system
    test_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test"  # Invalid test token
    result = validate_jwt_token(test_token)
    print(f"Test validation result: {result}")
    return result is None  # Should return None for invalid token


if __name__ == "__main__":
    # Run basic tests
    print("Testing JWT validation...")
    test_jwt_validation()
    print("JWT utilities loaded successfully")