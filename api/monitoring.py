"""
Comprehensive monitoring endpoint for Python backend
Provides detailed health, performance, and error monitoring
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path to import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from error_utils import (
        health_monitor, error_logger, send_success_response, 
        send_error_response, with_error_handling, APIError, ErrorTypes
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback implementations
    class MockHealthMonitor:
        def get_health_status(self):
            return {'status': 'unknown', 'error': 'Monitoring utilities not available'}
        def update_health_check(self):
            pass
    
    health_monitor = MockHealthMonitor()
    error_logger = None

try:
    from db_utils import test_connection, cleanup_connection
except ImportError:
    test_connection = None
    cleanup_connection = None

try:
    from auth_utils import get_jwt_secret
except ImportError:
    get_jwt_secret = None

class handler(BaseHTTPRequestHandler):
    
    @with_error_handling
    def do_GET(self):
        """Handle GET requests for monitoring data"""
        
        # Parse query parameters to determine what monitoring data to return
        query_params = self._parse_query_params()
        endpoint = query_params.get('endpoint', 'health')
        
        if endpoint == 'health':
            self._handle_health_check()
        elif endpoint == 'errors':
            self._handle_error_summary()
        elif endpoint == 'performance':
            self._handle_performance_metrics()
        elif endpoint == 'system':
            self._handle_system_info()
        elif endpoint == 'all':
            self._handle_comprehensive_monitoring()
        else:
            raise APIError(
                message=f"Unknown monitoring endpoint: {endpoint}",
                error_type=ErrorTypes.VALIDATION_ERROR,
                status_code=400
            )
    
    def _handle_health_check(self):
        """Handle basic health check"""
        
        # Update health monitor
        health_monitor.update_health_check()
        
        # Get basic health status
        health_status = health_monitor.get_health_status()
        
        # Test critical services
        services_status = self._test_critical_services()
        
        # Determine overall health
        overall_health = self._determine_overall_health(health_status, services_status)
        
        response_data = {
            'health': overall_health,
            'services': services_status,
            'monitoring': health_status
        }
        
        send_success_response(self, response_data, "Health check completed")
    
    def _handle_error_summary(self):
        """Handle error summary request"""
        
        if not error_logger:
            raise APIError(
                message="Error logging not available",
                error_type=ErrorTypes.INTERNAL_ERROR,
                status_code=503
            )
        
        error_summary = error_logger.get_error_summary()
        
        # Add recent error analysis
        recent_errors = self._analyze_recent_errors()
        
        response_data = {
            'error_summary': error_summary,
            'recent_analysis': recent_errors,
            'recommendations': self._get_error_recommendations(error_summary)
        }
        
        send_success_response(self, response_data, "Error summary generated")
    
    def _handle_performance_metrics(self):
        """Handle performance metrics request"""
        
        # Get system performance info
        performance_data = {
            'memory_usage': self._get_memory_usage(),
            'response_times': self._get_response_time_stats(),
            'throughput': self._get_throughput_stats(),
            'resource_utilization': self._get_resource_utilization()
        }
        
        send_success_response(self, performance_data, "Performance metrics generated")
    
    def _handle_system_info(self):
        """Handle system information request"""
        
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'environment': os.environ.get('VERCEL_ENV', 'development'),
            'deployment_region': os.environ.get('VERCEL_REGION', 'unknown'),
            'function_name': os.environ.get('VERCEL_FUNCTION_NAME', 'unknown'),
            'runtime': 'python',
            'dependencies': self._get_dependency_info(),
            'environment_variables': self._get_env_var_status(),
            'startup_time': datetime.now().isoformat()
        }
        
        send_success_response(self, system_info, "System information generated")
    
    def _handle_comprehensive_monitoring(self):
        """Handle comprehensive monitoring request with all data"""
        
        # Collect all monitoring data
        health_status = health_monitor.get_health_status()
        services_status = self._test_critical_services()
        overall_health = self._determine_overall_health(health_status, services_status)
        
        error_summary = error_logger.get_error_summary() if error_logger else {}
        recent_errors = self._analyze_recent_errors()
        
        performance_data = {
            'memory_usage': self._get_memory_usage(),
            'response_times': self._get_response_time_stats(),
            'throughput': self._get_throughput_stats()
        }
        
        system_info = {
            'python_version': sys.version,
            'environment': os.environ.get('VERCEL_ENV', 'development'),
            'deployment_region': os.environ.get('VERCEL_REGION', 'unknown')
        }
        
        comprehensive_data = {
            'health': overall_health,
            'services': services_status,
            'monitoring': health_status,
            'errors': {
                'summary': error_summary,
                'recent_analysis': recent_errors,
                'recommendations': self._get_error_recommendations(error_summary)
            },
            'performance': performance_data,
            'system': system_info,
            'timestamp': datetime.now().isoformat()
        }
        
        send_success_response(self, comprehensive_data, "Comprehensive monitoring data generated")
    
    def _test_critical_services(self):
        """Test critical services and return status"""
        
        services = {}
        
        # Test database connectivity
        if test_connection:
            try:
                db_result = test_connection()
                services['database'] = {
                    'status': 'healthy' if db_result.get('success') else 'unhealthy',
                    'details': db_result,
                    'last_tested': datetime.now().isoformat()
                }
            except Exception as e:
                services['database'] = {
                    'status': 'error',
                    'error': str(e),
                    'last_tested': datetime.now().isoformat()
                }
        else:
            services['database'] = {
                'status': 'unavailable',
                'error': 'Database utilities not loaded',
                'last_tested': datetime.now().isoformat()
            }
        
        # Test JWT authentication
        if get_jwt_secret:
            try:
                jwt_secret = get_jwt_secret()
                services['authentication'] = {
                    'status': 'healthy',
                    'jwt_configured': jwt_secret != 'fallback-secret-change-in-production',
                    'last_tested': datetime.now().isoformat()
                }
            except Exception as e:
                services['authentication'] = {
                    'status': 'error',
                    'error': str(e),
                    'last_tested': datetime.now().isoformat()
                }
        else:
            services['authentication'] = {
                'status': 'unavailable',
                'error': 'Auth utilities not loaded',
                'last_tested': datetime.now().isoformat()
            }
        
        # Test file system access
        try:
            test_file = '/tmp/health_check_test.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            services['filesystem'] = {
                'status': 'healthy',
                'last_tested': datetime.now().isoformat()
            }
        except Exception as e:
            services['filesystem'] = {
                'status': 'error',
                'error': str(e),
                'last_tested': datetime.now().isoformat()
            }
        
        return services
    
    def _determine_overall_health(self, health_status, services_status):
        """Determine overall health based on monitoring and services"""
        
        # Check if any critical services are down
        critical_services = ['database', 'authentication']
        critical_issues = []
        
        for service in critical_services:
            if service in services_status:
                if services_status[service]['status'] in ['error', 'unhealthy']:
                    critical_issues.append(service)
        
        # Determine status
        if critical_issues:
            status = 'degraded'
            message = f"Critical services have issues: {', '.join(critical_issues)}"
        elif health_status.get('error_rate_percent', 0) > 20:
            status = 'degraded'
            message = f"High error rate: {health_status.get('error_rate_percent', 0)}%"
        else:
            status = 'healthy'
            message = "All systems operational"
        
        return {
            'status': status,
            'message': message,
            'critical_issues': critical_issues,
            'last_checked': datetime.now().isoformat()
        }
    
    def _analyze_recent_errors(self):
        """Analyze recent errors for patterns"""
        
        if not error_logger or not hasattr(error_logger, 'last_errors'):
            return {'analysis': 'Error analysis not available'}
        
        recent_errors = error_logger.last_errors[-10:]  # Last 10 errors
        
        if not recent_errors:
            return {'analysis': 'No recent errors'}
        
        # Analyze error patterns
        error_types = {}
        error_messages = {}
        
        for error in recent_errors:
            error_type = error.get('error_type', 'unknown')
            error_message = error.get('message', 'unknown')[:50]  # First 50 chars
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            error_messages[error_message] = error_messages.get(error_message, 0) + 1
        
        return {
            'total_recent_errors': len(recent_errors),
            'error_type_distribution': error_types,
            'common_error_messages': dict(list(error_messages.items())[:5]),  # Top 5
            'last_error_time': recent_errors[-1].get('timestamp') if recent_errors else None,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _get_error_recommendations(self, error_summary):
        """Generate recommendations based on error patterns"""
        
        recommendations = []
        
        if not error_summary:
            return recommendations
        
        error_counts = error_summary.get('error_counts', {})
        
        # Check for common error patterns
        for error_key, count in error_counts.items():
            if 'Database' in error_key and count > 5:
                recommendations.append({
                    'type': 'database',
                    'message': 'High database error count detected. Check connection pool and query performance.',
                    'priority': 'high'
                })
            elif 'Timeout' in error_key and count > 3:
                recommendations.append({
                    'type': 'performance',
                    'message': 'Timeout errors detected. Consider optimizing slow operations.',
                    'priority': 'medium'
                })
            elif 'ValidationError' in error_key and count > 10:
                recommendations.append({
                    'type': 'validation',
                    'message': 'High validation error count. Review API documentation and client implementations.',
                    'priority': 'low'
                })
        
        return recommendations
    
    def _get_memory_usage(self):
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            return {'error': 'psutil not available for memory monitoring'}
    
    def _get_response_time_stats(self):
        """Get response time statistics"""
        # This would be enhanced with actual response time tracking
        return {
            'average_ms': 'Not implemented',
            'p95_ms': 'Not implemented',
            'p99_ms': 'Not implemented',
            'note': 'Response time tracking requires implementation'
        }
    
    def _get_throughput_stats(self):
        """Get throughput statistics"""
        health_status = health_monitor.get_health_status()
        uptime_hours = health_status.get('uptime_seconds', 0) / 3600
        
        if uptime_hours > 0:
            requests_per_hour = health_status.get('total_requests', 0) / uptime_hours
        else:
            requests_per_hour = 0
        
        return {
            'requests_per_hour': round(requests_per_hour, 2),
            'total_requests': health_status.get('total_requests', 0),
            'uptime_hours': round(uptime_hours, 2)
        }
    
    def _get_resource_utilization(self):
        """Get resource utilization information"""
        return {
            'cpu_percent': 'Not implemented',
            'memory_percent': 'See memory_usage',
            'disk_usage': 'Not applicable (serverless)',
            'note': 'Limited resource monitoring in serverless environment'
        }
    
    def _get_dependency_info(self):
        """Get information about loaded dependencies"""
        dependencies = {}
        
        # Check for key dependencies
        key_modules = ['psycopg2', 'jwt', 'docx', 'reportlab']
        
        for module in key_modules:
            try:
                __import__(module)
                dependencies[module] = 'loaded'
            except ImportError:
                dependencies[module] = 'not_available'
        
        return dependencies
    
    def _get_env_var_status(self):
        """Get status of critical environment variables"""
        critical_vars = ['DATABASE_URL', 'JWT_SECRET', 'VERCEL_ENV']
        
        env_status = {}
        for var in critical_vars:
            value = os.environ.get(var)
            env_status[var] = {
                'configured': value is not None,
                'length': len(value) if value else 0,
                'masked_value': f"{value[:4]}...{value[-4:]}" if value and len(value) > 8 else 'not_set'
            }
        
        return env_status
    
    def _parse_query_params(self):
        """Parse query parameters from the request path"""
        if '?' not in self.path:
            return {}
        
        query_string = self.path.split('?', 1)[1]
        params = {}
        
        for param in query_string.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        return params
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()