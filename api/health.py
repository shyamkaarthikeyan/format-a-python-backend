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
            
            # Import and use CORS utilities - no fallback
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from cors_utils import set_cors_headers
            origin = self.headers.get('Origin')
            set_cors_headers(self, origin)
            
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
    
    def do_POST(self):
        """Handle POST requests for advanced features"""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action', 'health')
            
            if action == 'health':
                # Return health status (same as GET)
                self.do_GET()
                return
                
            # ADVANCED FEATURES - BATCH PROCESSING
            elif action == 'batch_process':
                result = self._handle_batch_processing(data)
                self.send_success_response(result)
                
            # ADVANCED FEATURES - FILE SIZE VALIDATION
            elif action == 'validate_file':
                result = self._handle_file_validation(data)
                self.send_success_response(result)
                
            # ADVANCED FEATURES - MEMORY OPTIMIZATION
            elif action == 'optimize_memory':
                result = self._handle_memory_optimization()
                self.send_success_response(result)
                
            # ADVANCED FEATURES - TIMEOUT TESTING
            elif action == 'test_timeout':
                result = self._handle_timeout_testing(data)
                self.send_success_response(result)
                
            # ADVANCED FEATURES - ANALYTICS TRACKING
            elif action == 'track':
                result = self._handle_analytics_tracking(data)
                self.send_success_response(result)
                
            # ADVANCED FEATURES - PERFORMANCE METRICS
            elif action == 'performance':
                result = self._handle_performance_metrics()
                self.send_success_response(result)
                
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON", "Request body must be valid JSON")
        except Exception as e:
            self.send_error_response(500, "Processing error", str(e))
    
    def _handle_batch_processing(self, data):
        """Handle batch document processing"""
        import time
        import uuid
        
        documents = data.get('documents', [])
        user_id = data.get('user_id', 'anonymous')
        
        if not documents:
            raise ValueError("No documents provided")
        
        # Validate batch size (Vercel constraints)
        max_batch_size = 10
        if len(documents) > max_batch_size:
            raise ValueError(f"Batch size {len(documents)} exceeds maximum {max_batch_size}")
        
        # Import IEEE generator
        try:
            from ieee_generator_fixed import generate_ieee_document
        except ImportError:
            raise ImportError("IEEE generator not available")
        
        batch_id = str(uuid.uuid4())
        start_time = time.time()
        timeout_seconds = 8  # Leave 2 seconds buffer for Vercel's 10s limit
        
        results = []
        errors = []
        
        for i, doc_data in enumerate(documents):
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                errors.append({
                    'document_index': i,
                    'error': 'Batch processing timeout exceeded'
                })
                break
            
            try:
                # Process individual document
                doc_result = generate_ieee_document(
                    title=doc_data.get('title', 'Untitled'),
                    authors=doc_data.get('authors', []),
                    abstract=doc_data.get('abstract', ''),
                    sections=doc_data.get('sections', []),
                    format_type=doc_data.get('format', 'docx')
                )
                
                results.append({
                    'document_index': i,
                    'success': True,
                    'data': {
                        'file_data': doc_result.get('file_data'),
                        'file_size': doc_result.get('file_size', 0),
                        'format': doc_data.get('format', 'docx')
                    }
                })
                
            except Exception as e:
                errors.append({
                    'document_index': i,
                    'error': str(e)
                })
        
        processing_time = time.time() - start_time
        status = 'completed' if not errors else 'completed_with_errors'
        
        return {
            'batch_id': batch_id,
            'status': status,
            'progress': 100,
            'results': results,
            'errors': errors,
            'processing_time': processing_time,
            'documents_processed': len(results),
            'success_rate': (len(results) / len(documents)) * 100 if documents else 0
        }
    
    def _handle_file_validation(self, data):
        """Handle file size validation"""
        import base64
        
        file_data = data.get('file_data', '')
        file_type = data.get('file_type', 'unknown')
        
        # File size limits by type (in bytes)
        FILE_SIZE_LIMITS = {
            'docx': 25 * 1024 * 1024,  # 25MB for DOCX
            'pdf': 25 * 1024 * 1024,   # 25MB for PDF
            'image': 10 * 1024 * 1024, # 10MB for images
            'text': 5 * 1024 * 1024,   # 5MB for text files
            'json': 5 * 1024 * 1024    # 5MB for JSON data
        }
        
        MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB Vercel limit
        
        try:
            # Estimate decoded size (base64 is ~33% larger than original)
            estimated_size = len(file_data) * 3 // 4
            
            # Check estimated size first
            limit = FILE_SIZE_LIMITS.get(file_type, MAX_RESPONSE_SIZE // 2)
            if estimated_size > limit:
                return {
                    'valid': False,
                    'error': f'Estimated file size {estimated_size} bytes exceeds limit {limit} bytes',
                    'estimated_size': estimated_size,
                    'limit': limit
                }
            
            # Decode and validate actual size if reasonable
            if estimated_size < 10 * 1024 * 1024:  # Only decode if < 10MB
                try:
                    decoded_data = base64.b64decode(file_data)
                    actual_size = len(decoded_data)
                    
                    if actual_size > limit:
                        return {
                            'valid': False,
                            'error': f'File size {actual_size} bytes exceeds limit {limit} bytes',
                            'file_size': actual_size,
                            'limit': limit
                        }
                    
                    return {
                        'valid': True,
                        'file_size': actual_size,
                        'limit': limit,
                        'utilization': (actual_size / limit) * 100
                    }
                except Exception:
                    return {
                        'valid': False,
                        'error': 'Invalid base64 data',
                        'estimated_size': estimated_size
                    }
            else:
                return {
                    'valid': estimated_size <= limit,
                    'estimated_size': estimated_size,
                    'limit': limit,
                    'utilization': (estimated_size / limit) * 100,
                    'note': 'Size validation based on estimate (file too large to decode)'
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'File validation failed: {str(e)}'
            }
    
    def _handle_memory_optimization(self):
        """Handle memory optimization"""
        import gc
        
        try:
            # Force garbage collection
            gc.collect()
            
            # Try to get memory info if psutil is available
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # Estimate memory limit (Vercel typically allows ~1GB)
                memory_limit_mb = 1024
                memory_utilization = (memory_mb / memory_limit_mb) * 100
                
                return {
                    'optimized': True,
                    'memory_mb': round(memory_mb, 2),
                    'limit_mb': memory_limit_mb,
                    'utilization': round(memory_utilization, 2),
                    'recommendation': 'Memory optimized via garbage collection' if memory_utilization < 80 else 'High memory usage detected'
                }
                
            except ImportError:
                return {
                    'optimized': True,
                    'memory_mb': 'unknown',
                    'note': 'psutil not available for detailed memory monitoring',
                    'gc_collected': True
                }
                
        except Exception as e:
            return {
                'optimized': False,
                'error': f'Memory optimization failed: {str(e)}'
            }
    
    def _handle_timeout_testing(self, data):
        """Handle timeout testing"""
        import time
        
        duration = data.get('duration', 1.0)
        start_time = time.time()
        timeout_limit = 8.0  # Vercel safe limit
        
        try:
            if duration > timeout_limit:
                return {
                    'success': False,
                    'error': f'Requested duration {duration}s exceeds safe limit {timeout_limit}s',
                    'timeout_limit': timeout_limit,
                    'requested_duration': duration
                }
            
            # Simulate work for the specified duration
            time.sleep(min(duration, timeout_limit))
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'requested_duration': duration,
                'actual_duration': round(execution_time, 3),
                'timeout_limit': timeout_limit,
                'remaining_time': max(0, timeout_limit - execution_time),
                'message': f'Successfully completed {duration}s operation'
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'execution_time': round(execution_time, 3),
                'timeout_limit': timeout_limit
            }
    
    def _handle_analytics_tracking(self, data):
        """Handle analytics tracking"""
        import uuid
        
        # Simple in-memory analytics (for demonstration)
        user_id = data.get('user_id', 'anonymous')
        doc_type = data.get('doc_type', 'unknown')
        format_type = data.get('format_type', 'unknown')
        file_size = data.get('file_size', 0)
        processing_time = data.get('processing_time', 0.0)
        success = data.get('success', True)
        
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        return {
            'tracked': True,
            'session_id': session_id,
            'user_id': user_id,
            'doc_type': doc_type,
            'format_type': format_type,
            'file_size': file_size,
            'processing_time': processing_time,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_performance_metrics(self):
        """Handle performance metrics"""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                'system_metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'memory_used_mb': memory.used / (1024 * 1024)
                },
                'vercel_limits': {
                    'max_execution_time': 10,
                    'max_response_size_mb': 50,
                    'max_memory_mb': 1024
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except ImportError:
            return {
                'system_metrics': 'psutil not available',
                'vercel_limits': {
                    'max_execution_time': 10,
                    'max_response_size_mb': 50,
                    'max_memory_mb': 1024
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def send_success_response(self, data):
        """Send successful response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        
        # Import and use CORS utilities - no fallback
        from cors_utils import set_cors_headers
        origin = self.headers.get('Origin')
        set_cors_headers(self, origin)
        
        self.end_headers()
        
        response = {
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests - no fallback"""
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from cors_utils import handle_preflight
        origin = self.headers.get('Origin')
        handle_preflight(self, origin)
    
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