#!/usr/bin/env python3
"""
Verification script for Task 6: Deploy Python backend to Vercel with custom domain
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(url, method='GET', data=None, timeout=15):
    """Test a specific endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        elif method == 'OPTIONS':
            response = requests.options(url, timeout=timeout)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'headers': dict(response.headers)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def verify_deployment():
    """Verify the Python backend deployment"""
    
    # Production URL
    base_url = "https://format-a-python-backend.vercel.app"
    
    print("🚀 Verifying Python Backend Deployment")
    print(f"Base URL: {base_url}")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Health Check (Simple)
    print("\n1️⃣ Testing Simple Health Check...")
    result = test_endpoint(f"{base_url}/api/health-simple")
    if result['success'] and result['status_code'] == 200:
        health_data = result['response']
        print(f"✅ Health check passed")
        print(f"   Status: {health_data.get('status')}")
        print(f"   Environment: {health_data.get('system', {}).get('environment')}")
        print(f"   Missing vars: {health_data.get('missing_variables', [])}")
        tests.append(True)
    else:
        print(f"❌ Health check failed: {result.get('error', 'Unknown error')}")
        tests.append(False)
    
    # Test 2: Simple Test Endpoint
    print("\n2️⃣ Testing Simple Test Endpoint...")
    result = test_endpoint(f"{base_url}/api/test-simple")
    if result['success'] and result['status_code'] == 200:
        print(f"✅ Simple test passed")
        print(f"   Message: {result['response'].get('message')}")
        tests.append(True)
    else:
        print(f"❌ Simple test failed: {result.get('error', 'Unknown error')}")
        tests.append(False)
    
    # Test 3: Document Generator
    print("\n3️⃣ Testing Document Generator...")
    test_doc = {
        "title": "Deployment Verification Document",
        "authors": [{"name": "Verification Bot", "email": "test@example.com"}],
        "abstract": "This document verifies that the Python backend deployment is working correctly.",
        "keywords": "deployment, verification, python, backend",
        "sections": [
            {
                "title": "Introduction",
                "content": "This is a test document generated to verify the deployment."
            }
        ]
    }
    
    result = test_endpoint(f"{base_url}/api/document-generator", method='POST', data=test_doc)
    if result['success'] and result['status_code'] == 200:
        doc_data = result['response']
        print(f"✅ Document generator passed")
        print(f"   Success: {doc_data.get('success')}")
        print(f"   Preview type: {doc_data.get('preview_type')}")
        tests.append(True)
    else:
        print(f"❌ Document generator failed: {result.get('error', 'Unknown error')}")
        tests.append(False)
    
    # Test 4: CORS Configuration
    print("\n4️⃣ Testing CORS Configuration...")
    result = test_endpoint(f"{base_url}/api/health-simple", method='OPTIONS')
    if result['success'] and result['status_code'] == 200:
        cors_origin = result['headers'].get('access-control-allow-origin', '')
        cors_methods = result['headers'].get('access-control-allow-methods', '')
        
        print(f"✅ CORS configuration verified")
        print(f"   Allowed Origin: {cors_origin}")
        print(f"   Allowed Methods: {cors_methods}")
        
        # Check if format-a.vercel.app is allowed
        if cors_origin == '*' or 'format-a.vercel.app' in cors_origin:
            print(f"✅ CORS properly configured for main application")
            tests.append(True)
        else:
            print(f"⚠️  CORS may not allow main application access")
            tests.append(False)
    else:
        print(f"❌ CORS test failed: {result.get('error', 'Unknown error')}")
        tests.append(False)
    
    # Test 5: Environment Variables
    print("\n5️⃣ Testing Environment Variables...")
    result = test_endpoint(f"{base_url}/api/health-simple")
    if result['success'] and result['status_code'] == 200:
        env_vars = result['response'].get('environment_variables', {})
        required_vars = ['DATABASE_URL', 'JWT_SECRET', 'VITE_GOOGLE_CLIENT_ID']
        
        all_configured = all(env_vars.get(var) == 'configured' for var in required_vars)
        
        if all_configured:
            print(f"✅ All required environment variables configured")
            for var in required_vars:
                print(f"   {var}: {env_vars.get(var)}")
            tests.append(True)
        else:
            print(f"❌ Some environment variables missing")
            for var in required_vars:
                status = env_vars.get(var, 'unknown')
                print(f"   {var}: {status}")
            tests.append(False)
    else:
        print(f"❌ Environment variables test failed")
        tests.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Python backend is successfully deployed to Vercel")
        print("✅ All endpoints are working correctly")
        print("✅ Environment variables are configured")
        print("✅ CORS is properly set up")
        print("✅ Document generation is functional")
        
        print(f"\n🔗 Production URL: {base_url}")
        print("📋 Available Endpoints:")
        print(f"   • Health Check: {base_url}/api/health-simple")
        print(f"   • Simple Test: {base_url}/api/test-simple")
        print(f"   • Document Generator: {base_url}/api/document-generator")
        
        print("\n✨ Task 6 Completed Successfully!")
        print("The Python backend is ready for integration with the main Format-A application.")
        
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("Please check the failed tests above and resolve any issues.")
        return False

def main():
    """Main verification function"""
    try:
        success = verify_deployment()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())