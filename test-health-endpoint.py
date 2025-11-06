#!/usr/bin/env python3
"""
Test script to verify the health endpoint works
"""

import requests
import json
from datetime import datetime

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Python backend health endpoint...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    # Test the health endpoint
    url = "http://localhost:3001/api/health"
    
    try:
        print(f"Making request to: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint successful!")
            print(f"Response:")
            print(json.dumps(data, indent=2))
            
            # Check specific health indicators
            if data.get('success'):
                print("\n✅ Overall health: HEALTHY")
            else:
                print("\n⚠️ Overall health: UNHEALTHY")
                
            db_status = data.get('database', {})
            if db_status.get('success'):
                print(f"✅ Database: CONNECTED ({db_status.get('data', {}).get('responseTime', 'N/A')}ms)")
            else:
                print(f"❌ Database: FAILED - {db_status.get('error', {}).get('message', 'Unknown error')}")
                
            return True
            
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is Vercel dev running on port 3001?")
        print("Run: vercel dev --listen 3001")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_health_endpoint()
    if success:
        print("\n🎉 Health endpoint test passed!")
    else:
        print("\n💥 Health endpoint test failed!")