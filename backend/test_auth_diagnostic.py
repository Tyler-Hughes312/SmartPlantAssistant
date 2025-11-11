#!/usr/bin/env python3
"""
Quick authentication diagnostic
"""
import requests
import json

BASE_URL = 'http://localhost:5001'

print("=" * 70)
print("AUTHENTICATION DIAGNOSTIC")
print("=" * 70)

# Test 1: Check backend health
print("\n[1] Testing backend health...")
try:
    resp = requests.get(f'{BASE_URL}/api/health', timeout=5)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print("  ✅ Backend is running")
    else:
        print(f"  ❌ Backend returned {resp.status_code}")
except Exception as e:
    print(f"  ❌ Cannot reach backend: {e}")
    exit(1)

# Test 2: Test login
print("\n[2] Testing login endpoint...")
try:
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    resp = requests.post(
        f'{BASE_URL}/api/login',
        json=login_data,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"  Status Code: {resp.status_code}")
    print(f"  Response Headers:")
    for key, value in resp.headers.items():
        if 'cookie' in key.lower() or 'set-cookie' in key.lower():
            print(f"    {key}: {value[:100]}...")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"  ✅ Login successful!")
        print(f"  User: {data.get('user', {}).get('username', 'N/A')}")
        
        # Check if cookies were set
        cookies = resp.cookies
        if cookies:
            print(f"  ✅ Cookies received: {len(cookies)} cookie(s)")
            for cookie in cookies:
                print(f"    - {cookie.name}: {cookie.value[:50]}...")
        else:
            print(f"  ⚠️  No cookies received")
    else:
        print(f"  ❌ Login failed")
        print(f"  Response: {resp.text[:200]}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test with session
print("\n[3] Testing authenticated request...")
try:
    session = requests.Session()
    
    # Login first
    login_resp = session.post(
        f'{BASE_URL}/api/login',
        json={'username': 'testuser', 'password': 'testpass123'},
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    if login_resp.status_code == 200:
        print("  ✅ Login successful with session")
        
        # Try to get user info
        user_resp = session.get(f'{BASE_URL}/api/user', timeout=10)
        print(f"  GET /api/user Status: {user_resp.status_code}")
        
        if user_resp.status_code == 200:
            print("  ✅ Authenticated request works!")
        else:
            print(f"  ❌ Authenticated request failed: {user_resp.text[:200]}")
    else:
        print(f"  ❌ Login failed: {login_resp.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf login works here but not in browser:")
print("  1. Clear browser cookies (F12 → Application → Cookies)")
print("  2. Check browser console for errors")
print("  3. Check Network tab - look for CORS errors")
print("  4. Make sure you're using http://localhost:3001 (not 3000)")

