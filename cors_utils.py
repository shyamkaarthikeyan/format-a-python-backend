"""
CORS utilities for Format-A Python Backend
Handles cross-origin requests for both development and production
"""

import os
from typing import List, Optional

def get_allowed_origins() -> List[str]:
    """Get allowed origins from environment or use defaults"""
    # Production origins
    production_origins = [
        "https://format-a.vercel.app",
        "https://format-a-python-backend.vercel.app"
    ]
    
    # Development origins
    development_origins = [
        "http://localhost:5173",  # Vite dev server (main app)
        "http://localhost:3000",  # Alternative dev port
        "http://localhost:4173",  # Vite preview
        "http://localhost:3001",  # Python backend dev
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
        "http://127.0.0.1:3001"
    ]
    
    # Get custom origins from environment
    env_origins = os.environ.get('ALLOWED_ORIGINS', '')
    custom_origins = [origin.strip() for origin in env_origins.split(',') if origin.strip()]
    
    # Combine all origins
    all_origins = production_origins + development_origins + custom_origins
    
    # Remove duplicates while preserving order
    seen = set()
    unique_origins = []
    for origin in all_origins:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)
    
    return unique_origins

def is_origin_allowed(origin: Optional[str]) -> bool:
    """Check if an origin is allowed"""
    if not origin:
        return False
    
    allowed_origins = get_allowed_origins()
    
    # Allow all origins in development
    if os.environ.get('NODE_ENV') != 'production':
        return True
    
    return origin in allowed_origins

def get_cors_origin(request_origin: Optional[str]) -> str:
    """Get the appropriate CORS origin header value"""
    if is_origin_allowed(request_origin):
        return request_origin or "*"
    
    # Default to production origin if not allowed
    return "https://format-a.vercel.app"

def set_cors_headers(handler, origin: Optional[str] = None):
    """Set CORS headers on response"""
    cors_origin = get_cors_origin(origin)
    
    handler.send_header('Access-Control-Allow-Origin', cors_origin)
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Preview, X-Requested-With')
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.send_header('Access-Control-Max-Age', '86400')  # 24 hours

def handle_preflight(handler, origin: Optional[str] = None):
    """Handle CORS preflight requests"""
    handler.send_response(200)
    set_cors_headers(handler, origin)
    handler.end_headers()