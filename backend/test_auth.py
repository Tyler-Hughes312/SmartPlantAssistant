#!/usr/bin/env python3
"""
Comprehensive tests for authentication endpoints
Run with: python test_auth.py
"""

import sys
import os
import json
from unittest import TestCase

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

class AuthTestCase(TestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Use test database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key-for-testing'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Drop all and recreate tables (clean state)
        db.drop_all()
        db.create_all()
        
        # Create a test user with unique email
        test_user = User(
            username='testuser',
            email='testuser_unique@example.com',
            password_hash=generate_password_hash('testpass123'),
            location='Test City, ST',
            latitude=40.7128,
            longitude=-74.0060
        )
        db.session.add(test_user)
        db.session.commit()
        
        print("✓ Test database initialized")
        print(f"✓ Created test user: testuser / testpass123")
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_success(self):
        """Test successful login"""
        print("\n[TEST] Testing successful login...")
        response = self.app.post('/api/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'testuser')
        print("  ✓ Login successful test passed")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("\n[TEST] Testing login with invalid password...")
        response = self.app.post('/api/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        print("  ✓ Invalid credentials test passed")
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        print("\n[TEST] Testing login with missing password...")
        response = self.app.post('/api/login',
            data=json.dumps({
                'username': 'testuser'
            }),
            content_type='application/json'
        )
        
        print(f"  Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        print("  ✓ Missing fields test passed")
    
    def test_register_success(self):
        """Test successful registration"""
        print("\n[TEST] Testing successful registration...")
        response = self.app.post('/api/register',
            data=json.dumps({
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'location': 'Nashville, TN'
            }),
            content_type='application/json'
        )
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Registration successful')
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'newuser')
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        print("  ✓ Registration successful test passed")
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        print("\n[TEST] Testing registration with duplicate username...")
        response = self.app.post('/api/register',
            data=json.dumps({
                'username': 'testuser',  # Already exists
                'email': 'different@example.com',
                'password': 'pass123',
                'location': 'City, ST'
            }),
            content_type='application/json'
        )
        
        print(f"  Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        print("  ✓ Duplicate username test passed")
    
    def test_session_persistence(self):
        """Test that session persists after login"""
        print("\n[TEST] Testing session persistence...")
        
        # Login
        login_response = self.app.post('/api/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, 200)
        
        # Try to access protected endpoint
        user_response = self.app.get('/api/user')
        
        print(f"  Login Status: {login_response.status_code}")
        print(f"  User Endpoint Status: {user_response.status_code}")
        print(f"  User Response: {user_response.get_data(as_text=True)}")
        
        if user_response.status_code == 200:
            print("  ✓ Session persistence test passed")
        else:
            print("  ✗ Session persistence failed - cookies not working")
            print(f"     This indicates a session/cookie issue")
        
        self.assertEqual(user_response.status_code, 200)

def run_tests():
    """Run all tests"""
    import unittest
    
    print("=" * 60)
    print("SMART PLANT ASSISTANT - AUTHENTICATION TESTS")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(AuthTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
                print(f"    {traceback.split(chr(10))[-2]}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
                print(f"    {traceback.split(chr(10))[-2]}")
    
    print("=" * 60)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

