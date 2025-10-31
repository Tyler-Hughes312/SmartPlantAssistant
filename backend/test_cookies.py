#!/usr/bin/env python3
"""
Test cookie/session handling specifically
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5001'

def test_cookies():
    """Test cookie handling"""
    print("=" * 70)
    print("COOKIE/SESSION TEST")
    print("=" * 70)
    
    session = requests.Session()  # Use session to persist cookies
    
    # Test 1: Register
    print("\n[1] Registering new user...")
    try:
        reg_data = {
            'username': f'cookie_test_{hash(BASE_URL) % 100000}',
            'email': f'cookie_test_{hash(BASE_URL) % 100000}@test.com',
            'password': 'testpass123',
            'location': 'Nashville, TN'
        }
        
        response = session.post(
            f'{BASE_URL}/api/register',
            json=reg_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        print(f"  Cookies received: {list(response.cookies.keys())}")
        for cookie in response.cookies:
            print(f"    - {cookie.name}: {cookie.value[:50]}...")
            print(f"      Domain: {cookie.domain}, Path: {cookie.path}")
            print(f"      SameSite: {cookie.get('SameSite', 'Not set')}, Secure: {cookie.secure}")
        
        if response.status_code == 201:
            username = reg_data['username']
            print(f"  ✓ Registered: {username}")
            
            # Test 2: Login
            print(f"\n[2] Logging in as {username}...")
            login_response = session.post(
                f'{BASE_URL}/api/login',
                json={
                    'username': username,
                    'password': 'testpass123'
                },
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"  Status: {login_response.status_code}")
            print(f"  Response: {login_response.text[:200]}")
            print(f"  Cookies received: {list(login_response.cookies.keys())}")
            for cookie in login_response.cookies:
                print(f"    - {cookie.name}: {cookie.value[:50]}...")
                print(f"      Domain: {cookie.domain}, Path: {cookie.path}")
                print(f"      SameSite: {cookie.get('SameSite', 'Not set')}, Secure: {cookie.secure}")
            
            if login_response.status_code == 200:
                print(f"  ✓ Login successful!")
                
                # Test 3: Access protected endpoint
                print(f"\n[3] Accessing protected endpoint /api/user...")
                user_response = session.get(f'{BASE_URL}/api/user')
                
                print(f"  Status: {user_response.status_code}")
                print(f"  Response: {user_response.text[:200]}")
                print(f"  Cookies sent: {list(session.cookies.keys())}")
                
                if user_response.status_code == 200:
                    print(f"  ✓ Session working - cookies persist!")
                    return True
                else:
                    print(f"  ✗ Session not working - cookies may not be set correctly")
                    print(f"     This indicates a cookie/session issue")
                    return False
            else:
                print(f"  ✗ Login failed")
                return False
        else:
            print(f"  ⚠ Registration failed or user exists")
            # Try with existing testuser
            print(f"\n[2] Trying login with testuser...")
            login_response = session.post(
                f'{BASE_URL}/api/login',
                json={
                    'username': 'testuser',
                    'password': 'testpass123'
                },
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"  Status: {login_response.status_code}")
            print(f"  Cookies: {list(login_response.cookies.keys())}")
            if login_response.status_code == 200:
                user_response = session.get(f'{BASE_URL}/api/user')
                print(f"  /api/user Status: {user_response.status_code}")
                return user_response.status_code == 200
            
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Cannot connect to {BASE_URL}")
        print(f"     Make sure backend is running!")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_cookies()
    sys.exit(0 if success else 1)

