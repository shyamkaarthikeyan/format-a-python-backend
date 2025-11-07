#!/usr/bin/env python3
"""
Test script to verify the latest Python backend deployment
"""

import requests
import json
import sys

def test_latest_deployment():
    """Test the latest deployment URL"""
    # Latest deployment URL - Clean production URL
    base_url = "https://format-a-python-backend.vercel.app"
    
    print("🚀 Testing Latest Python Backend Deployment")
    print(f"Base URL: {base_url}")
    
    # Test simple health endpoint
    endpoints_to_test = [
        "/api/health-simple",
        "/api/test-simple",
        "/api/health"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n🧪 Testing {endpoint}: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ {endpoint} is working!")
                    print(f"Response preview: {json.dumps(data, indent=2)[:300]}...")
                    results.append(True)
                except json.JSONDecodeError:
                    print(f"⚠️  {endpoint} returned non-JSON response:")
                    print(response.text[:200])
                    results.append(False)
            else:
                print(f"❌ {endpoint} failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} request failed: {e}")
            results.append(False)
    
    # Test document generator
    print(f"\n🧪 Testing Document Generator")
    try:
        test_data = {
            "title": "Test IEEE Document",
            "authors": [{"name": "Test Author"}],
            "abstract": "Test abstract"
        }
        
        response = requests.post(f"{base_url}/api/document-generator", 
                               json=test_data, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document Generator is working!")
            print(f"Success: {data.get('success', False)}")
            results.append(True)
        else:
            print(f"❌ Document Generator failed: {response.status_code}")
            results.append(False)
            
    except Exception as e:
        print(f"❌ Document Generator failed: {e}")
        results.append(False)
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Python backend is working correctly.")
        print(f"\n✅ Production URL: {base_url}")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(test_latest_deployment())