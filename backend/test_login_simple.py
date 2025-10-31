#!/usr/bin/env python3
"""
Simple login test - will show the actual 500 error
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import check_password_hash

def test_login():
    """Test login directly"""
    print("=" * 70)
    print("SIMPLE LOGIN TEST")
    print("=" * 70)
    
    with app.app_context():
        # Find user
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            print("❌ User 'testuser' not found!")
            return False
        
        print(f"✓ User found: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Location: {getattr(user, 'location', 'N/A')}")
        print(f"  Latitude: {getattr(user, 'latitude', 'N/A')}")
        print(f"  Longitude: {getattr(user, 'longitude', 'N/A')}")
        
        # Test password
        password_valid = check_password_hash(user.password_hash, 'testpass123')
        print(f"  Password 'testpass123' valid: {password_valid}")
        
        if not password_valid:
            print("❌ Password check failed!")
            return False
        
        # Test response building (without session, just data structure)
        print("\nTesting response building...")
        try:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email or '',
                'location': getattr(user, 'location', None) or '',
                'latitude': getattr(user, 'latitude', None),
                'longitude': getattr(user, 'longitude', None)
            }
            print(f"✓ User data dict created: {user_data}")
            
            from flask import jsonify
            with app.app_context():
                response = jsonify({'message': 'Login successful', 'user': user_data})
                print(f"✓ jsonify() succeeded")
        except Exception as e:
            print(f"❌ Error during response building: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test full endpoint
        print("\nTesting full endpoint...")
        import json
        with app.test_client() as client:
            response = client.post('/api/login',
                data=json.dumps({"username": "testuser", "password": "testpass123"}),
                content_type='application/json'
            )
            
            print(f"Status Code: {response.status_code}")
            response_text = response.get_data(as_text=True)
            print(f"Response ({len(response_text)} chars):")
            print(response_text[:800])
            
            if response.status_code == 200:
                print("✅ LOGIN ENDPOINT WORKS!")
                try:
                    data = json.loads(response_text)
                    print(f"  User: {data.get('user', {}).get('username', 'N/A')}")
                except:
                    pass
                return True
            else:
                print(f"❌ LOGIN ENDPOINT FAILED: {response.status_code}")
                try:
                    error_data = json.loads(response_text)
                    if 'error_type' in error_data:
                        print(f"  Error Type: {error_data['error_type']}")
                    if 'details' in error_data:
                        print(f"  Details: {error_data['details']}")
                except:
                    pass
                return False

if __name__ == '__main__':
    success = test_login()
    sys.exit(0 if success else 1)

