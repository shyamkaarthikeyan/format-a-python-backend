"""
Comprehensive error handling and logging utilities for Python backend
Provides standardized error responses, logging, and monitoring capabilities
"""

import json
import logging
import traceback
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
from http.server import BaseHTTPRequestHandler

# Configure logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ErrorTypes:
    """Standard error types for consistent error handling"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class APIError(Exception):
    """Custom exception class for API errors with structured data"""
    
    def __init__(self, message: str, error_type: str = ErrorTypes.INTERNAL_ERROR, 
                 status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)

class ErrorLogger:
    """Centralized error logging with context and metrics"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = []
        self.max_stored_errors = 100
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None, 
                  request_info: Dict[str, Any] = None):
        """Log error with full context and stack trace"""
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'request_info': request_info or {},
            'stack_trace': traceback.format_exc()
        }
        
        # Log to console with structured format
        logger.error(f"ERROR: {error_data['error_type']} - {error_data['message']}")
        logger.error(f"Context: {json.dumps(error_data['context'], indent=2)}")
        logger.error(f"Stack trace: {error_data['stack_trace']}")
        
        # Track error counts for monitoring
        error_key = f"{error_data['error_type']}:{error_data['message'][:100]}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Store recent errors for health checks
        self.last_errors.append(error_data)
        if len(self.last_errors) > self.max_stored_errors:
            self.last_errors.pop(0)
        
        return error_data
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        return {
            'total_error_types': len(self.error_counts),
            'error_counts': dict(list(self.error_counts.items())[-10:]),  # Last 10 error types
            'recent_errors_count': len(self.last_errors),
            'last_error': self.last_errors[-1] if self.last_errors else None
        }

# Global error logger instance
error_logger = ErrorLogger()

def log_request_info(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    """Extract request information for logging"""
    return {
        'method': handler.command,
        'path': handler.path,
        'headers': dict(handler.headers),
        'client_address': handler.client_address[0] if handler.client_address else 'unknown',
        'user_agent': handler.headers.get('User-Agent', 'unknown'),
        'content_type': handler.headers.get('Content-Type', 'unknown'),
        'content_length': handler.headers.get('Content-Length', '0')
    }

def send_error_response(handler: BaseHTTPRequestHandler, error: Exception, 
                       context: Dict[str, Any] = None):
    """Send standardized error response with proper logging"""
    
    # Extract request info for logging
    request_info = log_request_info(handler)
    
    # Log the error with full context
    error_data = error_logger.log_error(error, context, request_info)
    
    # Determine status code and error type
    if isinstance(error, APIError):
        status_code = error.status_code
        error_type = error.error_type
        details = error.details
    else:
        status_code = 500
        error_type = ErrorTypes.INTERNAL_ERROR
        details = {}
    
    # Send response headers
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    
    # Add CORS headers
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from cors_utils import set_cors_headers
        origin = handler.headers.get('Origin')
        set_cors_headers(handler, origin)
    except ImportError:
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    handler.end_headers()
    
    # Create error response
    error_response = {
        'success': False,
        'error': {
            'type': error_type,
            'message': str(error),
            'details': details,
            'code': status_code,
            'timestamp': error_data['timestamp']
        },
        'request_id': error_data['timestamp'].replace(':', '').replace('-', '').replace('.', '')[:16]
    }
    
    # Add debug info in development
    if os.environ.get('VERCEL_ENV') != 'production':
        error_response['debug'] = {
            'stack_trace': error_data['stack_trace'],
            'context': context or {}
        }
    
    handler.wfile.write(json.dumps(error_response, indent=2).encode())

def send_success_response(handler: BaseHTTPRequestHandler, data: Any = None, 
                         message: str = None, status_code: int = 200):
    """Send standardized success response"""
    
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    
    # Add CORS headers
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from cors_utils import set_cors_headers
        origin = handler.headers.get('Origin')
        set_cors_headers(handler, origin)
    except ImportError:
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    handler.end_headers()
    
    response = {
        'success': True,
        'data': data,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    handler.wfile.write(json.dumps(response, indent=2).encode())

def with_error_handling(func):
    """Decorator to add comprehensive error handling to endpoint functions"""
    
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Log request start
            request_info = log_request_info(self)
            logger.info(f"Request started: {request_info['method']} {request_info['path']}")
            
            # Execute the function
            result = func(self, *args, **kwargs)
            
            # Log successful completion
            logger.info(f"Request completed successfully: {request_info['method']} {request_info['path']}")
            return result
            
        except APIError as api_error:
            # Handle known API errors
            context = {
                'function': func.__name__,
                'endpoint': getattr(self, 'path', 'unknown')
            }
            send_error_response(self, api_error, context)
            
        except json.JSONDecodeError as json_error:
            # Handle JSON parsing errors
            api_error = APIError(
                message="Invalid JSON in request body",
                error_type=ErrorTypes.VALIDATION_ERROR,
                status_code=400,
                details={'json_error': str(json_error)}
            )
            context = {
                'function': func.__name__,
                'endpoint': getattr(self, 'path', 'unknown'),
                'json_error': str(json_error)
            }
            send_error_response(self, api_error, context)
            
        except Exception as unexpected_error:
            # Handle unexpected errors
            api_error = APIError(
                message="Internal server error",
                error_type=ErrorTypes.INTERNAL_ERROR,
                status_code=500,
                details={'original_error': str(unexpected_error)}
            )
            context = {
                'function': func.__name__,
                'endpoint': getattr(self, 'path', 'unknown'),
                'unexpected_error': str(unexpected_error)
            }
            send_error_response(self, api_error, context)
    
    return wrapper

def validate_request_data(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate request data and raise APIError if validation fails"""
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise APIError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            error_type=ErrorTypes.VALIDATION_ERROR,
            status_code=400,
            details={'missing_fields': missing_fields}
        )

def timeout_handler(timeout_seconds: int = 30):
    """Decorator to add timeout handling to functions"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_signal_handler(signum, frame):
                raise APIError(
                    message=f"Operation timed out after {timeout_seconds} seconds",
                    error_type=ErrorTypes.TIMEOUT_ERROR,
                    status_code=408
                )
            
            # Set up timeout signal (Unix only)
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
                signal.alarm(timeout_seconds)
                
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancel the alarm
                    return result
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
            else:
                # Fallback for Windows/environments without SIGALRM
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

class HealthMonitor:
    """Health monitoring for the Python backend"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = None
    
    def record_request(self):
        """Record a request for monitoring"""
        self.request_count += 1
    
    def record_error(self):
        """Record an error for monitoring"""
        self.error_count += 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        error_rate = (self.error_count / max(self.request_count, 1)) * 100
        
        return {
            'status': 'healthy' if error_rate < 10 else 'degraded',
            'uptime_seconds': uptime,
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate_percent': round(error_rate, 2),
            'last_health_check': self.last_health_check,
            'error_summary': error_logger.get_error_summary(),
            'environment': os.environ.get('VERCEL_ENV', 'development'),
            'python_version': sys.version,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_health_check(self):
        """Update last health check timestamp"""
        self.last_health_check = datetime.now().isoformat()

# Global health monitor instance
health_monitor = HealthMonitor()

def log_performance(operation_name: str):
    """Decorator to log performance metrics"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f"Performance: {operation_name} completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.error(f"Performance: {operation_name} failed after {duration:.2f}ms - {str(e)}")
                raise
        
        return wrapper
    return decorator