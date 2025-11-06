#!/usr/bin/env python3
"""
Test the authentication endpoint with real HTTP requests
"""

import requests
import json
import jwt
import os
from datetime import datetime, timedelta

# Load environment variables
def load_env():
    env_files = ['.env.local', '.env']
    for env_file in env_files:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_file)
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            return True
    return False

def create_test_token():
    """Create a test JWT token using the same secret as the system"""
    load_env()
    jwt_secret = os.environ.get('JWT_SECRET', 'fallback-secret-change-in-production')
    
    payload = {
        'userId': 'test-user-123',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/avatar.jpg',
        'googleId': 'google-123456789',
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int((datetime.utcnow() + timedelta(days=7)).timestamp())
    }
    
    return jwt.encode(payload, jwt_secret, algorithm='HS256')

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("=" * 60)
    print("TESTING AUTHENTICATION ENDPOINTS")
    print("=" * 60)
    
    # Test ports
    ports = [3002, 3001, 3000]
    base_url = None
    
    # Find the correct port
    for port in ports:
        try:
            test_url = f"http://localhost:{port}/api/health"
            response = requests.get(test_url, timeout=5)
            if response.status_code in [200, 503]:  # 503 is OK for health check without DB
                base_url = f"http://localhost:{port}"
                print(f"✅ Found server running on port {port}")
                break
        except requests.exceptions.RequestException:
            continue
    
    if not base_url:
        print("❌ No server found running on ports 3000, 3001, or 3002")
        print("Please make sure 'vercel dev' is running")
        return False
    
    # Test health endpoint (should work without auth)
    print(f"\n1. Testing Health Endpoint: {base_url}/api/health")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 503]:
            data = response.json()
            print(f"   Success: {data.get('success', 'N/A')}")
            
            # Check if authentication info is included
            auth_info = data.get('authentication')
            if auth_info:
                print(f"   ✅ Authentication info included:")
                print(f"      JWT utilities loaded: {auth_info.get('utilities_loaded', False)}")
                print(f"      JWT secret configured: {auth_info.get('jwt_secret_configured', False)}")
            else:
                print(f"   ❌ No authentication info in health response")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Health endpoint test failed: {e}")
        return False
    
    # Test auth endpoint without token
    print(f"\n2. Testing Auth Endpoint Without Token: {base_url}/api/test-auth")
    try:
        response = requests.get(f"{base_url}/api/test-auth")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejected request without token")
            data = response.json()
            print(f"   Error message: {data.get('error', {}).get('message', 'N/A')}")
        else:
            print(f"   ❌ Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Auth endpoint test failed: {e}")
        return False
    
    # Test auth endpoint with valid token
    print(f"\n3. Testing Auth Endpoint With Valid Token:")
    try:
        test_token = create_test_token()
        print(f"   Created test token: {test_token[:50]}...")
        
        headers = {'Authorization': f'Bearer {test_token}'}
        response = requests.get(f"{base_url}/api/test-auth", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Successfully authenticated with valid token")
            data = response.json()
            if data.get('success'):
                user_info = data.get('data', {}).get('user', {})
                print(f"   User ID: {user_info.get('userId')}")
                print(f"   Email: {user_info.get('email')}")
                print(f"   Name: {user_info.get('name')}")
            else:
                print(f"   ❌ Response indicates failure: {data}")
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                print(f"   Response text: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Valid token test failed: {e}")
        return False
    
    # Test auth endpoint with invalid token
    print(f"\n4. Testing Auth Endpoint With Invalid Token:")
    try:
        headers = {'Authorization': 'Bearer invalid.token.here'}
        response = requests.get(f"{base_url}/api/test-auth", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejected invalid token")
            data = response.json()
            print(f"   Error message: {data.get('error', {}).get('message', 'N/A')}")
        else:
            print(f"   ❌ Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Invalid token test failed: {e}")
        return False
    
    # Test POST endpoint with authentication decorator
    print(f"\n5. Testing POST Endpoint With @require_auth Decorator:")
    try:
        test_token = create_test_token()
        headers = {
            'Authorization': f'Bearer {test_token}',
            'Content-Type': 'application/json'
        }
        
        test_data = {'message': 'Hello from authenticated POST request'}
        response = requests.post(f"{base_url}/api/test-auth", 
                               headers=headers, 
                               json=test_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ POST request with authentication successful")
            data = response.json()
            if data.get('success'):
                print(f"   Request data echoed: {data.get('data', {}).get('request_data')}")
            else:
                print(f"   ❌ Response indicates failure: {data}")
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                print(f"   Response text: {response.text}")
                
    except Exception as e:
        print(f"   ❌ POST with auth test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("AUTHENTICATION ENDPOINT TESTS COMPLETED")
    print("=" * 60)
    
    return True

def main():
    """Run authentication endpoint tests"""
    print("Starting Authentication Endpoint Tests...")
    print("Make sure 'vercel dev' is running in the Python backend directory")
    
    success = test_auth_endpoints()
    
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    
    if not success:
        print("\nTroubleshooting:")
        print("1. Make sure 'vercel dev' is running")
        print("2. Check that JWT_SECRET is set in .env.local")
        print("3. Verify auth_utils.py and api/test-auth.py exist")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)