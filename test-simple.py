#!/usr/bin/env python3
"""
Test the simple endpoint
"""

import requests
import json
from datetime import datetime

def test_simple_endpoint():
    """Test the simple endpoint"""
    print("🔍 Testing simple Python endpoint...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("-" * 50)
    
    url = "http://localhost:3001/api/test-simple"
    
    try:
        print(f"Making request to: {url}")
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Simple endpoint successful!")
            print(f"Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Simple endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_endpoint()
    if success:
        print("\n🎉 Simple endpoint test passed!")
    else:
        print("\n💥 Simple endpoint test failed!")