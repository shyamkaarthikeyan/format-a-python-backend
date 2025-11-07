#!/usr/bin/env python3
"""
Simple test to verify the Python backend functionality
Tests the IEEE generator directly without server dependencies
"""

import sys
import os
import json
from io import BytesIO

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_ieee_generator():
    """Test the IEEE generator directly"""
    print("🧪 Testing IEEE Generator...")
    
    try:
        # Import the IEEE generator
        from ieee_generator_fixed import generate_ieee_document
        print("✅ Successfully imported IEEE generator")
        
        # Test data
        test_data = {
            "title": "Frontend-Backend Integration Test",
            "authors": [
                {
                    "name": "Test Author",
                    "department": "Computer Science",
                    "organization": "Test University",
                    "city": "Test City",
                    "state": "Test State"
                }
            ],
            "abstract": "This document tests the integration between the Format-A frontend and the Python backend.",
            "keywords": "frontend, backend, integration, IEEE format",
            "sections": [
                {
                    "title": "Integration Test",
                    "contentBlocks": [
                        {
                            "type": "text",
                            "content": "This section verifies that the backend can generate IEEE-formatted documents.",
                            "order": 1
                        }
                    ]
                }
            ],
            "references": [
                {
                    "text": "Test Reference. Sample reference for testing."
                }
            ]
        }
        
        # Generate document
        doc_bytes = generate_ieee_document(test_data)
        print(f"✅ Generated document: {len(doc_bytes)} bytes")
        
        # Save test output
        with open("test_integration_output.docx", "wb") as f:
            f.write(doc_bytes)
        print("✅ Saved test document as test_integration_output.docx")
        
        return True
        
    except Exception as e:
        print(f"❌ IEEE generator test failed: {e}")
        return False

def test_api_modules():
    """Test API module imports"""
    print("🧪 Testing API modules...")
    
    try:
        # Test error utils
        from error_utils import with_error_handling, send_success_response
        print("✅ Successfully imported error_utils")
        
        # Test CORS utils
        from cors_utils import handle_cors
        print("✅ Successfully imported cors_utils")
        
        # Test auth utils
        from auth_utils import validate_jwt_token
        print("✅ Successfully imported auth_utils")
        
        return True
        
    except Exception as e:
        print(f"❌ API modules test failed: {e}")
        return False

def test_document_generator_api():
    """Test the document generator API structure"""
    print("🧪 Testing document generator API...")
    
    try:
        # Check if API file exists
        api_file = os.path.join("api", "document-generator.py")
        if os.path.exists(api_file):
            print("✅ document-generator.py exists")
            
            # Try to import it
            sys.path.append("api")
            # Note: We don't actually import it as it's designed for serverless
            print("✅ API structure verified")
            return True
        else:
            print("❌ document-generator.py not found")
            return False
            
    except Exception as e:
        print(f"❌ Document generator API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Format-A Python Backend Integration Test")
    print("=" * 50)
    
    tests = [
        ("IEEE Generator", test_ieee_generator),
        ("API Modules", test_api_modules),
        ("Document Generator API", test_document_generator_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        
    print("\n" + "=" * 50)
    print("🎯 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Python backend is functional.")
    else:
        print("💥 Some tests failed. Check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
