"""
Database utility functions for Python backend
Replicates the Neon database patterns from the Node.js backend
"""

import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Database connection manager that replicates the Neon database patterns
    from the Node.js backend
    """
    
    def __init__(self):
        self._connection = None
        self.connection_config = {
            'connect_timeout': 30,
            'command_timeout': 60,
            'max_retries': 3,
            'retry_delay': 1
        }
        
    def get_connection(self):
        """Get database connection with lazy initialization"""
        if not self._connection or self._connection.closed:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise Exception('DATABASE_URL environment variable is not set')
            
            try:
                self._connection = psycopg2.connect(
                    database_url,
                    cursor_factory=psycopg2.extras.RealDictCursor,
                    connect_timeout=self.connection_config['connect_timeout']
                )
                self._connection.autocommit = True
                logger.info("✅ Database connection established")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                raise
                
        return self._connection
    
    def close_connection(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

# Global database instance
db = DatabaseConnection()

def test_connection() -> Dict[str, Any]:
    """
    Test database connection and return health status
    Replicates the testConnection method from Node.js backend
    """
    start_time = datetime.now()
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        health_status = {
            'isHealthy': True,
            'lastChecked': datetime.now().isoformat(),
            'responseTime': response_time,
            'errorCount': 0,
            'testResult': result['test'] if result else None
        }
        
        logger.info(f"✅ Database connection test successful - {response_time:.2f}ms")
        return {
            'success': True,
            'data': health_status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        error_message = str(e)
        
        health_status = {
            'isHealthy': False,
            'lastChecked': datetime.now().isoformat(),
            'responseTime': response_time,
            'errorCount': 1,
            'lastError': error_message
        }
        
        logger.error(f"❌ Database connection test failed: {error_message}")
        return {
            'success': False,
            'error': {
                'message': 'Database connection test failed',
                'details': error_message,
                'code': 500
            },
            'data': health_status,
            'timestamp': datetime.now().isoformat()
        }

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user by ID - replicates getUserById from Node.js backend
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE id = %s LIMIT 1",
            (user_id,)
        )
        
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            # Convert to dict and handle JSON fields
            user_dict = dict(user)
            if user_dict.get('preferences') and isinstance(user_dict['preferences'], str):
                user_dict['preferences'] = json.loads(user_dict['preferences'])
            return user_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email - replicates getUserByEmail from Node.js backend
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE email = %s LIMIT 1",
            (email,)
        )
        
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            user_dict = dict(user)
            if user_dict.get('preferences') and isinstance(user_dict['preferences'], str):
                user_dict['preferences'] = json.loads(user_dict['preferences'])
            return user_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None

def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Get document by ID - replicates getDocumentById from Node.js backend
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT d.*, u.name as user_name, u.email as user_email
            FROM documents d
            LEFT JOIN users u ON d.user_id = u.id
            WHERE d.id = %s
            LIMIT 1
        """, (document_id,))
        
        document = cursor.fetchone()
        cursor.close()
        
        if document:
            doc_dict = dict(document)
            # Parse JSON content if it's a string
            if doc_dict.get('content') and isinstance(doc_dict['content'], str):
                doc_dict['content'] = json.loads(doc_dict['content'])
            return doc_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting document by ID {document_id}: {e}")
        return None

def record_download(download_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Record download - replicates recordDownload from Node.js backend
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Generate unique ID
        download_id = f"download_{int(datetime.now().timestamp() * 1000)}_{os.urandom(4).hex()}"
        
        cursor.execute("""
            INSERT INTO downloads (
                id, user_id, document_id, document_title, file_format, 
                file_size, downloaded_at, ip_address, user_agent, 
                status, email_sent, document_metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING *
        """, (
            download_id,
            download_data.get('user_id'),
            download_data.get('document_id'),
            download_data.get('document_title'),
            download_data.get('file_format'),
            download_data.get('file_size', 0),
            datetime.now(),
            download_data.get('ip_address'),
            download_data.get('user_agent'),
            'completed',
            False,
            json.dumps(download_data.get('document_metadata', {}))
        ))
        
        download = cursor.fetchone()
        cursor.close()
        
        if download:
            download_dict = dict(download)
            logger.info(f"✅ Download recorded: {download_data.get('document_title')}")
            return download_dict
        
        return None
        
    except Exception as e:
        logger.error(f"Error recording download: {e}")
        raise

def get_user_analytics() -> Dict[str, Any]:
    """
    Get user analytics - replicates getUserAnalytics from Node.js backend
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '1 day' THEN 1 END) as new_users_today,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as new_users_7d,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as new_users_30d,
                COUNT(CASE WHEN last_login_at >= NOW() - INTERVAL '7 days' THEN 1 END) as active_users_7d,
                COUNT(CASE WHEN last_login_at >= NOW() - INTERVAL '30 days' THEN 1 END) as active_users_30d,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_users
            FROM users
        """)
        
        analytics = cursor.fetchone()
        cursor.close()
        
        return dict(analytics) if analytics else {
            'total_users': 0,
            'new_users_today': 0,
            'new_users_7d': 0,
            'new_users_30d': 0,
            'active_users_7d': 0,
            'active_users_30d': 0,
            'active_users': 0
        }
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        return {
            'total_users': 0,
            'new_users_today': 0,
            'new_users_7d': 0,
            'new_users_30d': 0,
            'active_users_7d': 0,
            'active_users_30d': 0,
            'active_users': 0
        }

def safe_db_operation(operation_func, *args, **kwargs):
    """
    Wrapper for safe database operations with error handling
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            return operation_func(*args, **kwargs)
        except psycopg2.OperationalError as e:
            retry_count += 1
            logger.warning(f"Database operation failed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count >= max_retries:
                logger.error(f"Database operation failed after {max_retries} attempts")
                raise Exception(f"Database operation failed: {str(e)}")
            
            # Wait before retrying
            import time
            time.sleep(1 * retry_count)
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise

def cleanup_connection():
    """
    Cleanup database connection - useful for serverless functions
    """
    try:
        db.close_connection()
    except Exception as e:
        logger.warning(f"Error during connection cleanup: {e}")