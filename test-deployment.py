#!/usr/bin/env python3
"""
Test script to verify the Python backend deployment
"""

import requests
import json
import sys

def test_endpoint(url, endpoint_name):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing {endpoint_name}: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ {endpoint_name} is working!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"⚠️  {endpoint_name} returned non-JSON response:")
                print(response.text[:500])
                return False
        else:
            print(f"❌ {endpoint_name} failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {endpoint_name} request failed: {e}")
        return False

def test_document_generator(base_url):
    """Test the document generator endpoint"""
    url = f"{base_url}/api/document-generator"
    print(f"\n🧪 Testing Document Generator: {url}")
    
    test_data = {
        "title": "Test IEEE Document",
        "authors": [{"name": "Test Author", "email": "test@example.com"}],
        "abstract": "This is a test abstract for deployment verification.",
        "keywords": "test, deployment, verification",
        "sections": [
            {
                "title": "Introduction",
                "content": "This is a test introduction section."
            }
        ]
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Document Generator is working!")
                print(f"Success: {data.get('success', False)}")
                print(f"Preview Type: {data.get('preview_type', 'unknown')}")
                return True
            except json.JSONDecodeError:
                print(f"⚠️  Document Generator returned non-JSON response:")
                print(response.text[:500])
                return False
        else:
            print(f"❌ Document Generator failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Document Generator request failed: {e}")
        return False

def main():
    """Main test function"""
    # Get the latest deployment URL
    base_url = "https://format-a-python-backend-nw8v988ic-shyamkaarthikeyans-projects.vercel.app"
    
    print("🚀 Testing Python Backend Deployment")
    print(f"Base URL: {base_url}")
    
    # Test endpoints
    results = []
    
    # Test health endpoint
    results.append(test_endpoint(f"{base_url}/api/health", "Health Check"))
    
    # Test simple endpoint
    results.append(test_endpoint(f"{base_url}/api/test-simple", "Simple Test"))
    
    # Test document generator
    results.append(test_document_generator(base_url))
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Python backend is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())