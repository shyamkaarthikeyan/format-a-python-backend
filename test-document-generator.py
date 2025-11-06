#!/usr/bin/env python3
"""
Test script for the document-generator endpoint
"""

import requests
import json

# Test data for document generation
test_data = {
    "title": "Test IEEE Document",
    "authors": [
        {"name": "John Doe", "affiliation": "Test University"},
        {"name": "Jane Smith", "affiliation": "Research Institute"}
    ],
    "abstract": "This is a test abstract for the IEEE document generator.",
    "keywords": "test, IEEE, document, generator",
    "sections": [
        {
            "title": "Introduction",
            "content": "This is the introduction section of the test document."
        },
        {
            "title": "Methodology",
            "content": "This section describes the methodology used in the research."
        }
    ],
    "references": [
        {"text": "Test Reference 1, Journal of Testing, 2024."},
        {"text": "Test Reference 2, Conference on Testing, 2024."}
    ]
}

def test_local_endpoint():
    """Test the local development endpoint"""
    url = "http://localhost:3002/api/document-generator"
    
    try:
        response = requests.post(url, json=test_data, headers={
            'Content-Type': 'application/json'
        })
        
        print(f"Local test - Status Code: {response.status_code}")
        print(f"Local test - Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Local endpoint test passed!")
                return True
            else:
                print("❌ Local endpoint returned success=false")
                return False
        else:
            print("❌ Local endpoint test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Local endpoint test error: {e}")
        return False

def test_production_endpoint():
    """Test the production endpoint"""
    url = "https://format-a-python-backend-ok2my6t4o-shyamkaarthikeyans-projects.vercel.app/api/document-generator"
    
    try:
        response = requests.post(url, json=test_data, headers={
            'Content-Type': 'application/json',
            'Origin': 'https://format-a.vercel.app'
        })
        
        print(f"Production test - Status Code: {response.status_code}")
        print(f"Production test - Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Production endpoint test passed!")
                return True
            else:
                print("❌ Production endpoint returned success=false")
                return False
        else:
            print("❌ Production endpoint test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Production endpoint test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing document-generator endpoint...")
    print("=" * 50)
    
    # Test local endpoint
    local_success = test_local_endpoint()
    
    print("\n" + "=" * 50)
    print(f"Local endpoint: {'✅ PASSED' if local_success else '❌ FAILED'}")
    
    # Test production endpoint
    prod_success = test_production_endpoint()
    
    print("\n" + "=" * 50)
    print(f"Production endpoint: {'✅ PASSED' if prod_success else '❌ FAILED'}")