from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import time
import signal
import threading
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import functools

class TimeoutHandler:
    """Utility class for handling Vercel's 10-second execution limit"""
    
    VERCEL_TIMEOUT = 10  # Vercel's 10-second limit
    SAFE_TIMEOUT = 8     # Leave 2 seconds buffer
    
    def __init__(self):
        self.start_time = time.time()
        self.timeout_occurred = False
        self.timeout_callbacks = []
    
    def add_timeout_callback(self, callback: Callable):
        """Add a callback to execute when timeout is approaching"""
        self.timeout_callbacks.append(callback)
    
    def check_timeout(self) -> Dict[str, Any]:
        """Check if we're approaching timeout"""
        elapsed = time.time() - self.start_time
        remaining = self.SAFE_TIMEOUT - elapsed
        
        if remaining <= 0:
            self.timeout_occurred = True
            # Execute timeout callbacks
            for callback in self.timeout_callbacks:
                try:
                    callback()
                except Exception:
                    pass  # Ignore callback errors
        
        return {
            'elapsed': elapsed,
            'remaining': remaining,
            'timeout_occurred': self.timeout_occurred,
            'safe_timeout': self.SAFE_TIMEOUT,
            'vercel_timeout': self.VERCEL_TIMEOUT
        }
    
    def get_remaining_time(self) -> float:
        """Get remaining safe execution time"""
        elapsed = time.time() - self.start_time
        return max(0, self.SAFE_TIMEOUT - elapsed)
    
    def has_time_for_operation(self, estimated_seconds: float) -> bool:
        """Check if there's enough time for an operation"""
        remaining = self.get_remaining_time()
        return remaining >= estimated_seconds
    
    def execute_with_timeout(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute a function with timeout protection"""
        if self.timeout_occurred:
            return {
                'success': False,
                'error': 'Timeout already occurred',
                'timeout_info': self.check_timeout()
            }
        
        start_time = time.time()
        
        try:
            # Check if we have enough time
            if not self.has_time_for_operation(1.0):  # Need at least 1 second
                return {
                    'success': False,
                    'error': 'Insufficient time remaining for operation',
                    'timeout_info': self.check_timeout()
                }
            
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'timeout_info': self.check_timeout()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'timeout_info': self.check_timeout()
            }

def timeout_decorator(max_seconds: float = 8.0):
    """Decorator to add timeout protection to functions"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timeout_handler = TimeoutHandler()
            
            # Set up timeout signal (Unix only)
            def timeout_signal_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} exceeded {max_seconds} seconds")
            
            try:
                # Try to use signal for timeout (Unix systems)
                if hasattr(signal, 'SIGALRM'):
                    old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
                    signal.alarm(int(max_seconds))
                
                result = func(*args, **kwargs)
                
                # Cancel alarm
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                
                return result
                
            except TimeoutError as e:
                return {
                    'success': False,
                    'error': str(e),
                    'timeout_occurred': True
                }
            except Exception as e:
                # Cancel alarm on any exception
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                raise e
        
        return wrapper
    return decorator

class ProgressiveProcessor:
    """Process tasks progressively with timeout awareness"""
    
    def __init__(self, timeout_handler: TimeoutHandler):
        self.timeout_handler = timeout_handler
        self.results = []
        self.errors = []
        self.completed_count = 0
    
    def process_items(self, items: list, processor_func: Callable, 
                     estimated_time_per_item: float = 0.5) -> Dict[str, Any]:
        """Process items progressively with timeout awareness"""
        
        for i, item in enumerate(items):
            # Check if we have time for this item
            if not self.timeout_handler.has_time_for_operation(estimated_time_per_item):
                self.errors.append({
                    'item_index': i,
                    'error': 'Timeout: insufficient time for remaining items',
                    'remaining_items': len(items) - i
                })
                break
            
            try:
                start_time = time.time()
                result = processor_func(item)
                processing_time = time.time() - start_time
                
                self.results.append({
                    'item_index': i,
                    'result': result,
                    'processing_time': processing_time
                })
                self.completed_count += 1
                
                # Update estimated time based on actual processing
                if processing_time > estimated_time_per_item:
                    estimated_time_per_item = processing_time * 1.1  # Add 10% buffer
                
            except Exception as e:
                self.errors.append({
                    'item_index': i,
                    'error': str(e)
                })
        
        return {
            'completed_count': self.completed_count,
            'total_count': len(items),
            'success_rate': (self.completed_count / len(items)) * 100 if items else 0,
            'results': self.results,
            'errors': self.errors,
            'timeout_info': self.timeout_handler.check_timeout()
        }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        """Handle timeout-aware processing requests"""
        timeout_handler = TimeoutHandler()
        
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action', 'test')
            
            if action == 'test_timeout':
                # Test timeout handling
                duration = data.get('duration', 5.0)
                
                def long_running_task():
                    time.sleep(duration)
                    return f"Completed after {duration} seconds"
                
                result = timeout_handler.execute_with_timeout(long_running_task)
                self.send_success_response(result)
                
            elif action == 'progressive_process':
                # Test progressive processing
                items = data.get('items', list(range(10)))
                estimated_time = data.get('estimated_time_per_item', 0.5)
                
                def simple_processor(item):
                    # Simulate processing time
                    time.sleep(min(0.1, estimated_time))
                    return f"Processed item: {item}"
                
                processor = ProgressiveProcessor(timeout_handler)
                result = processor.process_items(items, simple_processor, estimated_time)
                self.send_success_response(result)
                
            elif action == 'check_timeout':
                # Check current timeout status
                timeout_info = timeout_handler.check_timeout()
                self.send_success_response(timeout_info)
                
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON", "Request body must be valid JSON")
        except Exception as e:
            timeout_info = timeout_handler.check_timeout()
            self.send_error_response(500, "Processing error", {
                'error': str(e),
                'timeout_info': timeout_info
            })
    
    def do_GET(self):
        """Handle timeout info requests"""
        try:
            timeout_handler = TimeoutHandler()
            
            info = {
                'vercel_timeout_limit': TimeoutHandler.VERCEL_TIMEOUT,
                'safe_timeout_limit': TimeoutHandler.SAFE_TIMEOUT,
                'current_timeout_info': timeout_handler.check_timeout(),
                'supported_actions': ['test_timeout', 'progressive_process', 'check_timeout'],
                'timeout_strategies': {
                    'progressive_processing': 'Process items one by one with timeout checks',
                    'early_termination': 'Stop processing when timeout approaches',
                    'chunked_responses': 'Split large responses into smaller chunks',
                    'async_processing': 'Use background processing for long tasks'
                }
            }
            
            self.send_success_response(info)
            
        except Exception as e:
            self.send_error_response(500, "Server error", str(e))
    
    def send_success_response(self, data):
        """Send successful response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def send_error_response(self, status_code, message, details=None):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'success': False,
            'error': {
                'message': message,
                'details': details,
                'code': status_code
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.wfile.write(json.dumps(response).encode())