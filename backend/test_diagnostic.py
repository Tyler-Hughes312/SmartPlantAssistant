#!/usr/bin/env python3
"""
Diagnostic tests to identify specific issues
Run this to diagnose login/registration problems
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def diagnostic_test():
    """Run diagnostic checks"""
    print("=" * 70)
    print("SMART PLANT ASSISTANT - DIAGNOSTIC TESTS")
    print("=" * 70)
    
    issues = []
    
    # 1. Check app initialization
    print("\n[1] Checking app initialization...")
    try:
        with app.app_context():
            print("  ✓ App initialized")
            print(f"  ✓ SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
            print(f"  ✓ SECRET_KEY length: {len(app.config.get('SECRET_KEY', ''))}")
            
            if not app.config.get('SECRET_KEY'):
                issues.append("SECRET_KEY not set")
    except Exception as e:
        issues.append(f"App initialization failed: {e}")
        print(f"  ✗ Error: {e}")
    
    # 2. Check database connection
    print("\n[2] Checking database connection...")
    try:
        with app.app_context():
            db.create_all()
            print("  ✓ Database connection OK")
            print(f"  ✓ Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            
            # Check if users table exists
            user_count = User.query.count()
            print(f"  ✓ Users in database: {user_count}")
            
            # List all users
            users = User.query.all()
            if users:
                print("  Users found:")
                for u in users:
                    print(f"    - {u.username} ({u.email})")
            else:
                print("  ⚠ No users in database")
    except Exception as e:
        issues.append(f"Database error: {e}")
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Test user creation and password checking
    print("\n[3] Testing user creation and password verification...")
    try:
        with app.app_context():
            # Test password hashing
            test_password = 'testpass123'
            password_hash = generate_password_hash(test_password)
            print(f"  ✓ Password hashing works")
            
            # Test password verification
            is_valid = check_password_hash(password_hash, test_password)
            print(f"  ✓ Password verification works: {is_valid}")
            
            if not is_valid:
                issues.append("Password verification not working")
            
            # Test with existing user
            test_user = User.query.filter_by(username='testuser').first()
            if test_user:
                print(f"  ✓ Found test user: {test_user.username}")
                is_valid_login = check_password_hash(test_user.password_hash, 'testpass123')
                print(f"  ✓ Test user password check: {is_valid_login}")
                
                if not is_valid_login:
                    issues.append("Test user password doesn't match")
    except Exception as e:
        issues.append(f"User creation test failed: {e}")
        print(f"  ✗ Error: {e}")
    
    # 4. Test login endpoint directly
    print("\n[4] Testing login endpoint with test client...")
    try:
        with app.test_client() as client:
            # Test login
            response = client.post('/api/login',
                data=json.dumps({
                    'username': 'testuser',
                    'password': 'testpass123'
                }),
                content_type='application/json'
            )
            
            print(f"  Status Code: {response.status_code}")
            response_data = response.get_data(as_text=True)
            print(f"  Response: {response_data[:300]}")
            
            if response.status_code == 200:
                print("  ✓ Login endpoint responds successfully")
                data = json.loads(response_data)
                if 'user' in data:
                    print(f"  ✓ User data returned: {data['user'].get('username')}")
            elif response.status_code == 401:
                print("  ⚠ Login returned 401 - checking user exists...")
                with app.app_context():
                    user = User.query.filter_by(username='testuser').first()
                    if not user:
                        issues.append("Test user 'testuser' doesn't exist in database")
                        print("    ✗ User 'testuser' not found")
                    else:
                        issues.append("Login failing even though user exists - check password")
                        print("    ✓ User exists but login failed - password issue?")
            else:
                issues.append(f"Login endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        issues.append(f"Login endpoint test failed: {e}")
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Test registration endpoint
    print("\n[5] Testing registration endpoint...")
    try:
        with app.app_context():
            # Delete test user if exists for registration test
            existing = User.query.filter_by(username='diagtest').first()
            if existing:
                db.session.delete(existing)
                db.session.commit()
        
        with app.test_client() as client:
            response = client.post('/api/register',
                data=json.dumps({
                    'username': 'diagtest',
                    'email': 'diagtest@example.com',
                    'password': 'diagpass123',
                    'location': 'Nashville, TN'
                }),
                content_type='application/json'
            )
            
            print(f"  Status Code: {response.status_code}")
            response_data = response.get_data(as_text=True)
            print(f"  Response: {response_data[:300]}")
            
            if response.status_code == 201:
                print("  ✓ Registration endpoint works")
            else:
                data = json.loads(response_data)
                if 'error' in data:
                    print(f"  ⚠ Registration error: {data['error']}")
                    issues.append(f"Registration failed: {data['error']}")
    except Exception as e:
        issues.append(f"Registration test failed: {e}")
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Check CORS configuration
    print("\n[6] Checking CORS configuration...")
    try:
        with app.test_client() as client:
            response = client.options('/api/login',
                headers={
                    'Origin': 'http://localhost:3001',
                    'Access-Control-Request-Method': 'POST'
                }
            )
            
            cors_headers = [k for k in response.headers.keys() if 'Access-Control' in k]
            if cors_headers:
                print(f"  ✓ CORS headers found: {cors_headers}")
            else:
                issues.append("CORS headers not present")
                print("  ⚠ No CORS headers found")
    except Exception as e:
        print(f"  ✗ Error checking CORS: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    if not issues:
        print("✓ No issues found - everything appears to be working correctly")
        print("\nIf login/registration still fails in the browser:")
        print("  1. Clear browser cookies")
        print("  2. Restart the backend server")
        print("  3. Check browser console for JavaScript errors")
        print("  4. Check Network tab for API call failures")
    else:
        print(f"✗ Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\nRecommended fixes:")
        if "SECRET_KEY not set" in str(issues):
            print("  - Set SECRET_KEY in .env file or ensure fixed dev key is used")
        if "User" in str(issues) and "doesn't exist" in str(issues):
            print("  - Run: python create_test_user.py")
        if "password" in str(issues).lower():
            print("  - Check that password hashing is working correctly")
        if "CORS" in str(issues):
            print("  - Verify CORS origins include http://localhost:3001")
    
    print("=" * 70)
    return len(issues) == 0

if __name__ == '__main__':
    success = diagnostic_test()
    sys.exit(0 if success else 1)

