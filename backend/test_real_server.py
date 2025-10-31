#!/usr/bin/env python3
"""
Test authentication against the real running server
Run this while the backend server is running on port 5001
"""

import requests
import json
import sys

BASE_URL = 'http://localhost:5001'

def test_real_login():
    """Test login against real server"""
    print("=" * 70)
    print("TESTING REAL SERVER - LOGIN/REGISTRATION")
    print("=" * 70)
    
    issues = []
    
    # Test 1: Health check
    print("\n[1] Testing health endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/api/health', timeout=5)
        if response.status_code == 200:
            print(f"  ✓ Server is running")
            print(f"  ✓ Health check passed: {response.json()}")
        else:
            issues.append(f"Health check failed: {response.status_code}")
            print(f"  ✗ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        issues.append("Cannot connect to server - is it running on port 5001?")
        print(f"  ✗ Cannot connect to {BASE_URL}")
        print(f"     Make sure backend is running: cd backend && python app.py")
        return False
    except Exception as e:
        issues.append(f"Health check error: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test 2: Try to register a new user
    print("\n[2] Testing registration endpoint...")
    test_username = f'testuser_real_{hash(BASE_URL) % 10000}'
    test_email = f'{test_username}@test.com'
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/register',
            json={
                'username': test_username,
                'email': test_email,
                'password': 'testpass123',
                'location': 'Nashville, TN'
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text[:300]}")
        
        if response.status_code == 201:
            print(f"  ✓ Registration successful!")
            data = response.json()
            if 'user' in data:
                print(f"  ✓ User created: {data['user']['username']}")
            
            # Test 3: Try to login with new user
            print(f"\n[3] Testing login with newly registered user...")
            login_response = requests.post(
                f'{BASE_URL}/api/login',
                json={
                    'username': test_username,
                    'password': 'testpass123'
                },
                headers={'Content-Type': 'application/json'},
                cookies=response.cookies,  # Use cookies from registration
                timeout=10
            )
            
            print(f"  Status Code: {login_response.status_code}")
            print(f"  Response: {login_response.text[:300]}")
            print(f"  Cookies received: {list(login_response.cookies.keys())}")
            
            if login_response.status_code == 200:
                print(f"  ✓ Login successful!")
                login_data = login_response.json()
                if 'user' in login_data:
                    print(f"  ✓ User data: {login_data['user']['username']}")
                
                # Test 4: Try to access protected endpoint
                print(f"\n[4] Testing protected endpoint (/api/user)...")
                user_response = requests.get(
                    f'{BASE_URL}/api/user',
                    cookies=login_response.cookies,
                    timeout=10
                )
                
                print(f"  Status Code: {user_response.status_code}")
                print(f"  Response: {user_response.text[:300]}")
                
                if user_response.status_code == 200:
                    print(f"  ✓ Session working - can access protected endpoint!")
                else:
                    issues.append("Session not persisting - cookies not working")
                    print(f"  ✗ Session not working - cookies may not be set correctly")
                    print(f"     This is likely a CORS/cookie issue")
            else:
                issues.append(f"Login failed: {login_response.status_code}")
                print(f"  ✗ Login failed")
                
        elif response.status_code == 400:
            data = response.json()
            if 'error' in data:
                if 'already exists' in data['error'].lower():
                    print(f"  ⚠ User already exists - that's OK")
                    print(f"\n[3] Testing login with existing user...")
                    login_response = requests.post(
                        f'{BASE_URL}/api/login',
                        json={
                            'username': test_username,
                            'password': 'testpass123'
                        },
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    print(f"  Status Code: {login_response.status_code}")
                    if login_response.status_code == 200:
                        print(f"  ✓ Login with existing user works!")
                    else:
                        issues.append("Login with existing user failed")
                else:
                    issues.append(f"Registration validation error: {data['error']}")
        else:
            issues.append(f"Registration failed: {response.status_code}")
            print(f"  ✗ Registration failed")
            
    except Exception as e:
        issues.append(f"Registration test error: {e}")
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Test with existing user "test"
    print(f"\n[5] Testing login with existing user 'test'...")
    try:
        # First try to get the password - we'll need to check what it is
        # For now, just test if the endpoint responds
        login_response = requests.post(
            f'{BASE_URL}/api/login',
            json={
                'username': 'test',
                'password': 'wrongpassword'  # Intentionally wrong to test error handling
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"  Status Code: {login_response.status_code}")
        if login_response.status_code == 401:
            print(f"  ✓ Login endpoint responds correctly to wrong password")
        elif login_response.status_code == 200:
            print(f"  ⚠ Login succeeded - password might be 'wrongpassword'")
    except Exception as e:
        print(f"  ✗ Error testing login: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("✓ ALL TESTS PASSED - Server is working correctly!")
        print("\nIf login/registration fails in browser:")
        print("  1. Clear browser cookies")
        print("  2. Check browser console for JavaScript errors")
        print("  3. Check Network tab for API call details")
    else:
        print(f"✗ Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    print("=" * 70)
    return len(issues) == 0

if __name__ == '__main__':
    success = test_real_server()
    sys.exit(0 if success else 1)

