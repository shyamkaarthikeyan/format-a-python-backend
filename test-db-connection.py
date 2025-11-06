#!/usr/bin/env python3
"""
Test script to verify database connectivity
Tests the db_utils module and database connection
"""

import os
import sys
from datetime import datetime

# Load environment variables from .env.local if it exists
def load_env():
    env_files = ['.env.local', '.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"Loading environment from {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            break
    else:
        print("No .env file found, using system environment variables")

def test_database_connection():
    """Test database connection and operations"""
    print("🔍 Testing Python backend database connectivity...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Load environment
    load_env()
    
    # Check if DATABASE_URL is configured
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    print(f"✅ DATABASE_URL configured: {database_url[:50]}...")
    
    try:
        # Import and test db_utils
        from db_utils import test_connection, get_user_analytics, db
        
        print("\n1. Testing basic database connection...")
        result = test_connection()
        
        if result['success']:
            print("✅ Database connection successful!")
            print(f"   Response time: {result['data']['responseTime']:.2f}ms")
            print(f"   Health status: {result['data']['isHealthy']}")
        else:
            print("❌ Database connection failed!")
            print(f"   Error: {result['error']['message']}")
            print(f"   Details: {result['error']['details']}")
            return False
        
        print("\n2. Testing user analytics query...")
        analytics = get_user_analytics()
        print("✅ User analytics retrieved:")
        for key, value in analytics.items():
            print(f"   {key}: {value}")
        
        print("\n3. Testing connection cleanup...")
        db.close_connection()
        print("✅ Connection cleanup successful")
        
        print("\n🎉 All database tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)