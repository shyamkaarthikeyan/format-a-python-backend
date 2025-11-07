from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db_utils import get_db_connection
except ImportError:
    def get_db_connection():
        return None

class DocumentAnalytics:
    """Document processing analytics and usage tracking"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.utcnow()
        self.metrics = {
            'documents_generated': 0,
            'total_processing_time': 0.0,
            'total_file_size': 0,
            'error_count': 0,
            'success_count': 0,
            'format_breakdown': {},
            'user_sessions': set(),
            'peak_memory_usage': 0,
            'average_processing_time': 0.0
        }
    
    def track_document_generation(self, user_id: str, doc_type: str, format_type: str, 
                                file_size: int, processing_time: float, success: bool) -> Dict[str, Any]:
        """Track document generation metrics"""
        
        # Update metrics
        self.metrics['documents_generated'] += 1
        self.metrics['total_processing_time'] += processing_time
        self.metrics['total_file_size'] += file_size
        self.metrics['user_sessions'].add(user_id)
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
        
        # Track format breakdown
        format_key = f"{doc_type}_{format_type}"
        if format_key not in self.metrics['format_breakdown']:
            self.metrics['format_breakdown'][format_key] = {
                'count': 0,
                'total_size': 0,
                'total_time': 0.0,
                'success_rate': 0.0
            }
        
        format_metrics = self.metrics['format_breakdown'][format_key]
        format_metrics['count'] += 1
        format_metrics['total_size'] += file_size
        format_metrics['total_time'] += processing_time
        
        if format_metrics['count'] > 0:
            success_count = format_metrics.get('success_count', 0)
            if success:
                success_count += 1
                format_metrics['success_count'] = success_count
            format_metrics['success_rate'] = (success_count / format_metrics['count']) * 100
        
        # Update average processing time
        if self.metrics['documents_generated'] > 0:
            self.metrics['average_processing_time'] = (
                self.metrics['total_processing_time'] / self.metrics['documents_generated']
            )
        
        # Store in database if available
        try:
            self._store_analytics_record(user_id, doc_type, format_type, file_size, 
                                       processing_time, success)
        except Exception as e:
            print(f"Failed to store analytics: {e}")
        
        return {
            'tracked': True,
            'session_id': self.session_id,
            'current_metrics': self.get_current_metrics()
        }
    
    def _store_analytics_record(self, user_id: str, doc_type: str, format_type: str,
                              file_size: int, processing_time: float, success: bool):
        """Store analytics record in database"""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Create analytics table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_analytics (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255),
                    user_id VARCHAR(255),
                    doc_type VARCHAR(100),
                    format_type VARCHAR(50),
                    file_size INTEGER,
                    processing_time FLOAT,
                    success BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert analytics record
            cursor.execute("""
                INSERT INTO document_analytics 
                (session_id, user_id, doc_type, format_type, file_size, processing_time, success)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.session_id, user_id, doc_type, format_type, file_size, processing_time, success))
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            print(f"Database analytics error: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current session metrics"""
        session_duration = (datetime.utcnow() - self.session_start).total_seconds()
        
        return {
            'session_id': self.session_id,
            'session_duration_seconds': session_duration,
            'documents_generated': self.metrics['documents_generated'],
            'success_rate': (
                (self.metrics['success_count'] / max(1, self.metrics['documents_generated'])) * 100
            ),
            'total_file_size_mb': self.metrics['total_file_size'] / (1024 * 1024),
            'average_processing_time': self.metrics['average_processing_time'],
            'unique_users': len(self.metrics['user_sessions']),
            'format_breakdown': self.metrics['format_breakdown'],
            'throughput_docs_per_minute': (
                (self.metrics['documents_generated'] / max(1, session_duration)) * 60
            )
        }
    
    def get_historical_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get historical analytics from database"""
        conn = get_db_connection()
        if not conn:
            return {'error': 'Database connection not available'}
        
        try:
            cursor = conn.cursor()
            
            # Get analytics for the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(processing_time) as avg_processing_time,
                    SUM(file_size) as total_file_size,
                    COUNT(CASE WHEN success THEN 1 END) as successful_generations,
                    doc_type,
                    format_type
                FROM document_analytics 
                WHERE created_at >= %s
                GROUP BY doc_type, format_type
                ORDER BY total_documents DESC
            """, (start_date,))
            
            results = cursor.fetchall()
            
            # Get daily breakdown
            cursor.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as documents,
                    COUNT(DISTINCT user_id) as users,
                    AVG(processing_time) as avg_time,
                    SUM(file_size) as total_size
                FROM document_analytics 
                WHERE created_at >= %s
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (start_date,))
            
            daily_results = cursor.fetchall()
            
            cursor.close()
            
            # Format results
            format_breakdown = []
            for row in results:
                format_breakdown.append({
                    'doc_type': row[6],
                    'format_type': row[7],
                    'total_documents': row[0],
                    'unique_users': row[1],
                    'unique_sessions': row[2],
                    'avg_processing_time': float(row[3]) if row[3] else 0,
                    'total_file_size_mb': (row[4] / (1024 * 1024)) if row[4] else 0,
                    'success_rate': (row[5] / row[0] * 100) if row[0] > 0 else 0
                })
            
            daily_breakdown = []
            for row in daily_results:
                daily_breakdown.append({
                    'date': row[0].isoformat() if row[0] else None,
                    'documents': row[1],
                    'users': row[2],
                    'avg_processing_time': float(row[3]) if row[3] else 0,
                    'total_size_mb': (row[4] / (1024 * 1024)) if row[4] else 0
                })
            
            return {
                'period_days': days,
                'format_breakdown': format_breakdown,
                'daily_breakdown': daily_breakdown,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Failed to retrieve analytics: {str(e)}'}
        finally:
            if conn:
                conn.close()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance and optimization metrics"""
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'system_metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_mb': memory.available / (1024 * 1024),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024 * 1024 * 1024)
                },
                'processing_metrics': self.get_current_metrics(),
                'recommendations': self._get_performance_recommendations()
            }
            
        except ImportError:
            return {
                'system_metrics': 'psutil not available',
                'processing_metrics': self.get_current_metrics(),
                'recommendations': self._get_performance_recommendations()
            }
    
    def _get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        if self.metrics['average_processing_time'] > 2.0:
            recommendations.append("Consider optimizing document generation for faster processing")
        
        if self.metrics['error_count'] > 0:
            error_rate = (self.metrics['error_count'] / max(1, self.metrics['documents_generated'])) * 100
            if error_rate > 10:
                recommendations.append(f"High error rate ({error_rate:.1f}%) - investigate common failure causes")
        
        avg_file_size = self.metrics['total_file_size'] / max(1, self.metrics['documents_generated'])
        if avg_file_size > 10 * 1024 * 1024:  # 10MB
            recommendations.append("Large average file size - consider compression or optimization")
        
        if len(self.metrics['format_breakdown']) > 5:
            recommendations.append("Many format types in use - consider standardizing on fewer formats")
        
        return recommendations

# Global analytics instance
analytics = DocumentAnalytics()

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        """Handle analytics tracking requests and advanced features"""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            action = data.get('action', 'track')
            
            if action == 'track':
                # Track document generation
                user_id = data.get('user_id', 'anonymous')
                doc_type = data.get('doc_type', 'unknown')
                format_type = data.get('format_type', 'unknown')
                file_size = data.get('file_size', 0)
                processing_time = data.get('processing_time', 0.0)
                success = data.get('success', True)
                
                result = analytics.track_document_generation(
                    user_id, doc_type, format_type, file_size, processing_time, success
                )
                
                self.send_success_response(result)
                
            elif action == 'metrics':
                # Get current metrics
                metrics = analytics.get_current_metrics()
                self.send_success_response(metrics)
                
            elif action == 'performance':
                # Get performance metrics
                performance = analytics.get_performance_metrics()
                self.send_success_response(performance)
                
            # ADVANCED FEATURES - BATCH PROCESSING
            elif action == 'batch_process':
                # Handle batch document processing
                documents = data.get('documents', [])
                user_id = data.get('user_id', 'anonymous')
                
                if not documents:
                    self.send_error_response(400, "No documents provided", "Documents array is required")
                    return
                
                # Validate batch size (Vercel constraints)
                max_batch_size = 10
                if len(documents) > max_batch_size:
                    self.send_error_response(400, "Batch too large", f"Maximum {max_batch_size} documents per batch")
                    return
                
                # Process batch with timeout awareness
                batch_result = self._process_document_batch(documents, user_id)
                self.send_success_response(batch_result)
                
            # ADVANCED FEATURES - FILE SIZE VALIDATION
            elif action == 'validate_file':
                # Validate file size and handle Vercel's 50MB limit
                file_data = data.get('file_data', '')
                file_type = data.get('file_type', 'unknown')
                
                validation_result = self._validate_file_size(file_data, file_type)
                self.send_success_response(validation_result)
                
            # ADVANCED FEATURES - MEMORY OPTIMIZATION
            elif action == 'optimize_memory':
                # Perform memory optimization
                memory_info = self._optimize_memory()
                self.send_success_response(memory_info)
                
            # ADVANCED FEATURES - TIMEOUT TESTING
            elif action == 'test_timeout':
                # Test timeout handling
                duration = data.get('duration', 1.0)
                timeout_result = self._test_timeout_handling(duration)
                self.send_success_response(timeout_result)
                
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON", "Request body must be valid JSON")
        except Exception as e:
            self.send_error_response(500, "Analytics error", str(e))
    
    def _process_document_batch(self, documents: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
        """Process a batch of documents with timeout and memory awareness"""
        import time
        import base64
        
        # Import IEEE generator
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from ieee_generator_fixed import generate_ieee_document
        except ImportError:
            return {
                'batch_id': str(uuid.uuid4()),
                'status': 'failed',
                'error': 'IEEE generator not available',
                'results': [],
                'errors': [{'error': 'IEEE generator import failed'}]
            }
        
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
                
                # Track analytics
                analytics.track_document_generation(
                    user_id, 'ieee', doc_data.get('format', 'docx'),
                    doc_result.get('file_size', 0), time.time() - start_time, True
                )
                
            except Exception as e:
                errors.append({
                    'document_index': i,
                    'error': str(e)
                })
                
                # Track failed generation
                analytics.track_document_generation(
                    user_id, 'ieee', doc_data.get('format', 'docx'),
                    0, time.time() - start_time, False
                )
        
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
    
    def _validate_file_size(self, file_data: str, file_type: str) -> Dict[str, Any]:
        """Validate file size against Vercel's 50MB limit"""
        import base64
        
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
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization and return memory info"""
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
    
    def _test_timeout_handling(self, duration: float) -> Dict[str, Any]:
        """Test timeout handling with specified duration"""
        import time
        
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
    
    def do_GET(self):
        """Handle analytics retrieval requests"""
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            action = query_params.get('action', ['current'])[0]
            
            if action == 'current':
                # Get current session metrics
                metrics = analytics.get_current_metrics()
                self.send_success_response(metrics)
                
            elif action == 'historical':
                # Get historical analytics
                days = int(query_params.get('days', [7])[0])
                historical = analytics.get_historical_analytics(days)
                self.send_success_response(historical)
                
            elif action == 'performance':
                # Get performance metrics
                performance = analytics.get_performance_metrics()
                self.send_success_response(performance)
                
            elif action == 'info':
                # Get analytics info
                info = {
                    'session_id': analytics.session_id,
                    'session_start': analytics.session_start.isoformat(),
                    'supported_actions': ['track', 'metrics', 'performance'],
                    'supported_queries': ['current', 'historical', 'performance', 'info'],
                    'tracking_features': [
                        'Document generation counts',
                        'Processing times',
                        'File sizes',
                        'Success/error rates',
                        'Format breakdown',
                        'User sessions',
                        'Performance metrics'
                    ]
                }
                self.send_success_response(info)
                
            else:
                self.send_error_response(400, "Invalid action", f"Action '{action}' not supported")
                
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