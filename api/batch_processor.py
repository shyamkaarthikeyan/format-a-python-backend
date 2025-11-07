from http.server import BaseHTTPRequestHandler
import json
import os
import time
import threading
from datetime import datetime
from typing import List, Dict, Any
import uuid
import sys
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ieee_generator_fixed import generate_ieee_document
except ImportError:
    def generate_ieee_document(*args, **kwargs):
        return {"error": "IEEE generator not available"}

class BatchProcessor:
    def __init__(self):
        self.batch_jobs = {}
        self.max_batch_size = 10  # Limit batch size for Vercel constraints
        self.timeout_seconds = 8  # Leave 2 seconds buffer for Vercel's 10s limit
        
    def create_batch_job(self, documents: List[Dict[str, Any]], user_id: str) -> str:
        """Create a new batch processing job"""
        batch_id = str(uuid.uuid4())
        
        # Validate batch size
        if len(documents) > self.max_batch_size:
            raise ValueError(f"Batch size {len(documents)} exceeds maximum {self.max_batch_size}")
        
        # Estimate processing time and memory usage
        estimated_time = len(documents) * 0.5  # 500ms per document estimate
        if estimated_time > self.timeout_seconds:
            raise ValueError(f"Estimated processing time {estimated_time}s exceeds limit {self.timeout_seconds}s")
        
        self.batch_jobs[batch_id] = {
            'id': batch_id,
            'user_id': user_id,
            'documents': documents,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'completed_at': None,
            'results': [],
            'errors': [],
            'progress': 0
        }
        
        return batch_id
    
    def process_batch(self, batch_id: str) -> Dict[str, Any]:
        """Process a batch of documents"""
        if batch_id not in self.batch_jobs:
            raise ValueError(f"Batch job {batch_id} not found")
        
        job = self.batch_jobs[batch_id]
        job['status'] = 'processing'
        
        start_time = time.time()
        results = []
        errors = []
        
        try:
            for i, doc_data in enumerate(job['documents']):
                # Check timeout
                if time.time() - start_time > self.timeout_seconds:
                    errors.append({
                        'document_index': i,
                        'error': 'Batch processing timeout exceeded'
                    })
                    break
                
                try:
                    # Process individual document
                    result = self._process_single_document(doc_data)
                    results.append({
                        'document_index': i,
                        'success': True,
                        'data': result
                    })
                except Exception as e:
                    errors.append({
                        'document_index': i,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
                
                # Update progress
                job['progress'] = int((i + 1) / len(job['documents']) * 100)
        
        except Exception as e:
            job['status'] = 'failed'
            job['errors'] = [{'error': str(e), 'traceback': traceback.format_exc()}]
            return job
        
        job['results'] = results
        job['errors'] = errors
        job['status'] = 'completed' if not errors else 'completed_with_errors'
        job['completed_at'] = datetime.utcnow().isoformat()
        job['progress'] = 100
        
        return job
    
    def _process_single_document(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document with memory optimization"""
        try:
            # Validate document data size
            doc_size = len(json.dumps(doc_data).encode('utf-8'))
            if doc_size > 1024 * 1024:  # 1MB limit per document
                raise ValueError(f"Document data size {doc_size} bytes exceeds 1MB limit")
            
            # Generate document based on type
            doc_type = doc_data.get('type', 'ieee')
            
            if doc_type == 'ieee':
                result = generate_ieee_document(
                    title=doc_data.get('title', 'Untitled'),
                    authors=doc_data.get('authors', []),
                    abstract=doc_data.get('abstract', ''),
                    sections=doc_data.get('sections', []),
                    format_type=doc_data.get('format', 'docx')
                )
                
                return {
                    'type': doc_type,
                    'format': doc_data.get('format', 'docx'),
                    'file_data': result.get('file_data'),
                    'file_size': result.get('file_size', 0),
                    'generated_at': datetime.utcnow().isoformat()
                }
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
                
        except Exception as e:
            raise Exception(f"Document processing failed: {str(e)}")
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get the status of a batch job"""
        if batch_id not in self.batch_jobs:
            raise ValueError(f"Batch job {batch_id} not found")
        
        return self.batch_jobs[batch_id]
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old batch jobs to prevent memory leaks"""
        current_time = datetime.utcnow()
        jobs_to_remove = []
        
        for batch_id, job in self.batch_jobs.items():
            created_at = datetime.fromisoformat(job['created_at'])
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                jobs_to_remove.append(batch_id)
        
        for batch_id in jobs_to_remove:
            del self.batch_jobs[batch_id]

# Global batch processor instance
batch_processor = BatchProcessor()

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        """Handle batch processing requests"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 10 * 1024 * 1024:  # 10MB limit
                self.send_error_response(413, "Request too large", "Maximum request size is 10MB")
                return
            
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action', 'create')
            
            if action == 'create':
                # Create new batch job
                documents = data.get('documents', [])
                user_id = data.get('user_id', 'anonymous')
                
                if not documents:
                    self.send_error_response(400, "No documents provided", "Documents array is required")
                    return
                
                batch_id = batch_processor.create_batch_job(documents, user_id)
                
                # Start processing in background (for async processing)
                # Note: In serverless, we process synchronously due to stateless nature
                result = batch_processor.process_batch(batch_id)
                
                self.send_success_response({
                    'batch_id': batch_id,
                    'status': result['status'],
                    'progress': result['progress'],
                    'results': result['results'],
                    'errors': result['errors']
                })
                
            elif action == 'status':
                # Get batch status
                batch_id = data.get('batch_id')
                if not batch_id:
                    self.send_error_response(400, "Batch ID required", "batch_id parameter is required")
                    return
                
                status = batch_processor.get_batch_status(batch_id)
                self.send_success_response(status)
                
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
        except ValueError as e:
            self.send_error_response(400, "Validation error", str(e))
        except Exception as e:
            self.send_error_response(500, "Processing error", str(e))
    
    def do_GET(self):
        """Handle batch status queries"""
        try:
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            batch_id = query_params.get('batch_id', [None])[0]
            
            if not batch_id:
                self.send_error_response(400, "Batch ID required", "batch_id query parameter is required")
                return
            
            status = batch_processor.get_batch_status(batch_id)
            self.send_success_response(status)
            
        except ValueError as e:
            self.send_error_response(404, "Batch not found", str(e))
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