#!/usr/bin/env python3
"""
Direct test of login endpoint - simulates what browser does
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5001'

def test_login():
    """Test login with testuser"""
    print("=" * 70)
    print("DIRECT LOGIN TEST")
    print("=" * 70)
    
    session = requests.Session()
    
    # Test login
    print("\n[1] Testing login with testuser/testpass123...")
    try:
        response = session.post(
            f'{BASE_URL}/api/login',
            json={
                'username': 'testuser',
                'password': 'testpass123'
            },
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3001'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if 'cookie' in key.lower() or 'set-cookie' in key.lower():
                print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        print(response.text)
        
        print(f"\nCookies Received:")
        for cookie in session.cookies:
            print(f"  Name: {cookie.name}")
            print(f"  Value: {cookie.value[:50]}...")
            print(f"  Domain: {cookie.domain}")
            print(f"  Path: {cookie.path}")
            print(f"  Secure: {cookie.secure}")
        
        if response.status_code == 200:
            print("\n✅ LOGIN SUCCESSFUL!")
            
            # Test protected endpoint
            print("\n[2] Testing protected endpoint /api/user...")
            user_response = session.get(f'{BASE_URL}/api/user')
            
            print(f"Status Code: {user_response.status_code}")
            print(f"Response: {user_response.text[:200]}")
            
            if user_response.status_code == 200:
                print("✅ SESSION WORKING - Protected endpoint accessible!")
                return True
            else:
                print("❌ SESSION NOT WORKING - Cookie not being sent")
                print(f"Cookies in session: {list(session.cookies.keys())}")
                return False
        else:
            print(f"\n❌ LOGIN FAILED")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('error', 'Unknown error')}")
            except:
                pass
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Make sure backend is running: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_login()
    sys.exit(0 if success else 1)



