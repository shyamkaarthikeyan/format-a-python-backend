from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import base64
import tempfile

class FileValidator:
    """Utility class for file size validation and memory optimization"""
    
    # Vercel limits
    MAX_RESPONSE_SIZE = 50 * 1024 * 1024  # 50MB response limit
    MAX_MEMORY_USAGE = 1024 * 1024 * 1024  # 1GB memory limit (estimated)
    MAX_EXECUTION_TIME = 10  # 10 seconds
    
    # File size limits by type
    FILE_SIZE_LIMITS = {
        'docx': 25 * 1024 * 1024,  # 25MB for DOCX
        'pdf': 25 * 1024 * 1024,   # 25MB for PDF
        'image': 10 * 1024 * 1024, # 10MB for images
        'text': 5 * 1024 * 1024,   # 5MB for text files
        'json': 5 * 1024 * 1024    # 5MB for JSON data
    }
    
    @classmethod
    def validate_file_size(cls, file_data: bytes, file_type: str) -> Dict[str, Any]:
        """Validate file size against limits"""
        file_size = len(file_data)
        limit = cls.FILE_SIZE_LIMITS.get(file_type, cls.MAX_RESPONSE_SIZE // 2)
        
        if file_size > limit:
            return {
                'valid': False,
                'error': f'File size {file_size} bytes exceeds limit {limit} bytes for type {file_type}',
                'file_size': file_size,
                'limit': limit
            }
        
        if file_size > cls.MAX_RESPONSE_SIZE:
            return {
                'valid': False,
                'error': f'File size {file_size} bytes exceeds Vercel response limit {cls.MAX_RESPONSE_SIZE} bytes',
                'file_size': file_size,
                'limit': cls.MAX_RESPONSE_SIZE
            }
        
        return {
            'valid': True,
            'file_size': file_size,
            'limit': limit,
            'utilization': (file_size / limit) * 100
        }
    
    @classmethod
    def validate_base64_data(cls, base64_data: str, file_type: str) -> Dict[str, Any]:
        """Validate base64 encoded file data"""
        try:
            # Estimate decoded size (base64 is ~33% larger than original)
            estimated_size = len(base64_data) * 3 // 4
            
            # Check estimated size first
            limit = cls.FILE_SIZE_LIMITS.get(file_type, cls.MAX_RESPONSE_SIZE // 2)
            if estimated_size > limit:
                return {
                    'valid': False,
                    'error': f'Estimated file size {estimated_size} bytes exceeds limit {limit} bytes',
                    'estimated_size': estimated_size,
                    'limit': limit
                }
            
            # Decode and validate actual size
            file_data = base64.b64decode(base64_data)
            return cls.validate_file_size(file_data, file_type)
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Invalid base64 data: {str(e)}',
                'estimated_size': len(base64_data) * 3 // 4
            }
    
    @classmethod
    def optimize_memory_usage(cls, data: Any) -> Dict[str, Any]:
        """Optimize memory usage for large data processing"""
        try:
            import psutil
            import gc
            
            # Get current memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Force garbage collection
            gc.collect()
            
            # Check if we're approaching memory limits
            memory_limit_mb = cls.MAX_MEMORY_USAGE / 1024 / 1024
            memory_utilization = (memory_mb / memory_limit_mb) * 100
            
            if memory_utilization > 80:
                return {
                    'optimized': False,
                    'warning': f'High memory usage: {memory_mb:.1f}MB ({memory_utilization:.1f}%)',
                    'memory_mb': memory_mb,
                    'limit_mb': memory_limit_mb,
                    'recommendation': 'Consider processing smaller batches or reducing data size'
                }
            
            return {
                'optimized': True,
                'memory_mb': memory_mb,
                'limit_mb': memory_limit_mb,
                'utilization': memory_utilization
            }
            
        except ImportError:
            # psutil not available, use basic optimization
            gc.collect()
            return {
                'optimized': True,
                'memory_mb': 'unknown',
                'note': 'psutil not available for detailed memory monitoring'
            }
        except Exception as e:
            return {
                'optimized': False,
                'error': f'Memory optimization failed: {str(e)}'
            }
    
    @classmethod
    def create_chunked_response(cls, large_data: bytes, chunk_size: int = 1024 * 1024) -> Dict[str, Any]:
        """Create chunked response for large files"""
        total_size = len(large_data)
        
        if total_size <= cls.MAX_RESPONSE_SIZE:
            return {
                'chunked': False,
                'data': base64.b64encode(large_data).decode('utf-8'),
                'size': total_size
            }
        
        # Create chunks
        chunks = []
        for i in range(0, total_size, chunk_size):
            chunk = large_data[i:i + chunk_size]
            chunks.append(base64.b64encode(chunk).decode('utf-8'))
        
        return {
            'chunked': True,
            'total_chunks': len(chunks),
            'total_size': total_size,
            'chunk_size': chunk_size,
            'chunks': chunks[:5],  # Return first 5 chunks, rest via separate requests
            'message': f'File too large ({total_size} bytes), split into {len(chunks)} chunks'
        }
    
    @classmethod
    def validate_request_size(cls, request_data: bytes) -> Dict[str, Any]:
        """Validate incoming request size"""
        request_size = len(request_data)
        
        # Vercel has a 50MB request limit
        if request_size > cls.MAX_RESPONSE_SIZE:
            return {
                'valid': False,
                'error': f'Request size {request_size} bytes exceeds limit {cls.MAX_RESPONSE_SIZE} bytes',
                'size': request_size,
                'limit': cls.MAX_RESPONSE_SIZE
            }
        
        return {
            'valid': True,
            'size': request_size,
            'limit': cls.MAX_RESPONSE_SIZE,
            'utilization': (request_size / cls.MAX_RESPONSE_SIZE) * 100
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
        """Handle file validation requests"""
        try:
            # Get request size
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Validate request size before reading
            if content_length > FileValidator.MAX_RESPONSE_SIZE:
                self.send_error_response(413, "Request too large", 
                    f"Request size {content_length} exceeds limit {FileValidator.MAX_RESPONSE_SIZE}")
                return
            
            # Read and parse request
            post_data = self.rfile.read(content_length)
            request_validation = FileValidator.validate_request_size(post_data)
            
            if not request_validation['valid']:
                self.send_error_response(413, "Request too large", request_validation['error'])
                return
            
            data = json.loads(post_data.decode('utf-8'))
            action = data.get('action', 'validate')
            
            if action == 'validate_file':
                # Validate file data
                file_data = data.get('file_data', '')
                file_type = data.get('file_type', 'unknown')
                
                if not file_data:
                    self.send_error_response(400, "No file data provided", "file_data is required")
                    return
                
                # Validate base64 data
                validation_result = FileValidator.validate_base64_data(file_data, file_type)
                
                # Add memory optimization info
                memory_info = FileValidator.optimize_memory_usage(file_data)
                validation_result['memory_info'] = memory_info
                
                self.send_success_response(validation_result)
                
            elif action == 'optimize_memory':
                # Perform memory optimization
                memory_info = FileValidator.optimize_memory_usage(data)
                self.send_success_response(memory_info)
                
            elif action == 'chunk_file':
                # Create chunked response for large file
                file_data = data.get('file_data', '')
                chunk_size = data.get('chunk_size', 1024 * 1024)  # 1MB default
                
                if not file_data:
                    self.send_error_response(400, "No file data provided", "file_data is required")
                    return
                
                try:
                    decoded_data = base64.b64decode(file_data)
                    chunked_result = FileValidator.create_chunked_response(decoded_data, chunk_size)
                    self.send_success_response(chunked_result)
                except Exception as e:
                    self.send_error_response(400, "Invalid file data", str(e))
                    
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON", "Request body must be valid JSON")
        except Exception as e:
            self.send_error_response(500, "Validation error", str(e))
    
    def do_GET(self):
        """Handle file validation info requests"""
        try:
            # Return file size limits and validation info
            info = {
                'file_size_limits': FileValidator.FILE_SIZE_LIMITS,
                'max_response_size': FileValidator.MAX_RESPONSE_SIZE,
                'max_memory_usage': FileValidator.MAX_MEMORY_USAGE,
                'max_execution_time': FileValidator.MAX_EXECUTION_TIME,
                'supported_actions': ['validate_file', 'optimize_memory', 'chunk_file'],
                'memory_info': FileValidator.optimize_memory_usage(None)
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