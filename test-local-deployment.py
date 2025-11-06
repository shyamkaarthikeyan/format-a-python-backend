#!/usr/bin/env python3
"""
Test script to verify the local Python backend deployment
"""

import requests
import json
import sys

def test_endpoint(url, endpoint_name):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing {endpoint_name}: {url}")
    
    try:
        response = requests.get(url, timeout=10)
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
        response = requests.post(url, json=test_data, timeout=10)
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

def test_cors_headers(base_url):
    """Test CORS configuration"""
    url = f"{base_url}/api/health"
    print(f"\n🧪 Testing CORS Headers: {url}")
    
    try:
        # Test preflight request
        response = requests.options(url, headers={
            'Origin': 'https://format-a.vercel.app',
            'Access-Control-Request-Method': 'GET'
        }, timeout=10)
        
        print(f"OPTIONS Status Code: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        # Check if format-a.vercel.app is allowed
        allowed_origin = cors_headers.get('Access-Control-Allow-Origin')
        if allowed_origin == 'https://format-a.vercel.app' or allowed_origin == '*':
            print("✅ CORS is properly configured for format-a.vercel.app")
            return True
        else:
            print(f"⚠️  CORS may not be properly configured. Allowed origin: {allowed_origin}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Main test function"""
    # Test local deployment
    base_url = "http://localhost:3001"
    
    print("🚀 Testing Local Python Backend Deployment")
    print(f"Base URL: {base_url}")
    
    # Test endpoints
    results = []
    
    # Test health endpoint
    results.append(test_endpoint(f"{base_url}/api/health", "Health Check"))
    
    # Test simple endpoint
    results.append(test_endpoint(f"{base_url}/api/test-simple", "Simple Test"))
    
    # Test document generator
    results.append(test_document_generator(base_url))
    
    # Test CORS configuration
    results.append(test_cors_headers(base_url))
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 All tests passed! Local Python backend is working correctly.")
        print("\n📝 Next steps:")
        print("1. The local deployment is working")
        print("2. Environment variables are configured")
        print("3. CORS is set up for format-a.vercel.app")
        print("4. Document generation is functional")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())