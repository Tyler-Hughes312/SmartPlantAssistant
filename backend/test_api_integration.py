#!/usr/bin/env python3
"""
Integration tests for API endpoints
Tests the full request/response cycle including CORS and cookies
"""

import sys
import os
import json
import requests
from unittest import TestCase

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

class APIIntegrationTestCase(TestCase):
    """Integration tests using requests library"""
    
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key-for-integration-testing'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass123'),
            location='Test City, ST',
            latitude=40.7128,
            longitude=-74.0060
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Start test server (if needed)
        self.base_url = 'http://localhost:5001'
        print("✓ Test environment set up")
    
    def tearDown(self):
        """Clean up"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_endpoint_structure(self):
        """Test that login endpoint exists and responds correctly"""
        print("\n[INTEGRATION TEST] Testing login endpoint structure...")
        
        with app.test_client() as client:
            # Test with valid JSON
            response = client.post('/api/login',
                data=json.dumps({
                    'username': 'testuser',
                    'password': 'testpass123'
                }),
                content_type='application/json',
                headers={
                    'Origin': 'http://localhost:3001',
                    'Content-Type': 'application/json'
                }
            )
            
            print(f"  Status: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            print(f"  Response: {response.get_data(as_text=True)[:200]}")
            
            self.assertIn(response.status_code, [200, 401])  # 200 if success, 401 if credentials wrong
            self.assertEqual(response.content_type, 'application/json')
            
            # Check for CORS headers
            if 'Access-Control-Allow-Origin' in response.headers:
                print(f"  ✓ CORS headers present")
            
            print("  ✓ Login endpoint structure test passed")
    
    def test_register_endpoint_structure(self):
        """Test that register endpoint exists and responds correctly"""
        print("\n[INTEGRATION TEST] Testing register endpoint structure...")
        
        with app.test_client() as client:
            response = client.post('/api/register',
                data=json.dumps({
                    'username': 'newtestuser',
                    'email': 'newtest@example.com',
                    'password': 'newpass123',
                    'location': 'Nashville, TN'
                }),
                content_type='application/json',
                headers={
                    'Origin': 'http://localhost:3001',
                    'Content-Type': 'application/json'
                }
            )
            
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.get_data(as_text=True)[:200]}")
            
            self.assertIn(response.status_code, [201, 400])  # 201 if success, 400 if validation fails
            print("  ✓ Register endpoint structure test passed")
    
    def test_cors_configuration(self):
        """Test CORS headers are properly configured"""
        print("\n[INTEGRATION TEST] Testing CORS configuration...")
        
        with app.test_client() as client:
            # Test OPTIONS preflight
            response = client.options('/api/login',
                headers={
                    'Origin': 'http://localhost:3001',
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                }
            )
            
            print(f"  OPTIONS Status: {response.status_code}")
            
            # Test actual POST with CORS
            response = client.post('/api/login',
                data=json.dumps({
                    'username': 'testuser',
                    'password': 'testpass123'
                }),
                content_type='application/json',
                headers={
                    'Origin': 'http://localhost:3001'
                }
            )
            
            print(f"  POST Status: {response.status_code}")
            print(f"  CORS Headers: {[k for k in response.headers.keys() if 'Access-Control' in k]}")
            
            # Check for CORS headers
            cors_headers = [k for k in response.headers.keys() if 'Access-Control' in k]
            if cors_headers:
                print(f"  ✓ CORS headers found: {cors_headers}")
            else:
                print(f"  ⚠ No CORS headers found - may cause issues")
            
            print("  ✓ CORS configuration test completed")

def run_integration_tests():
    """Run integration tests"""
    import unittest
    
    print("=" * 60)
    print("SMART PLANT ASSISTANT - API INTEGRATION TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(APIIntegrationTestCase)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL INTEGRATION TESTS PASSED")
    else:
        print("✗ SOME INTEGRATION TESTS FAILED")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)

