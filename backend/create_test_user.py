#!/usr/bin/env python3
"""Script to create a test user for login"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_test_user():
    """Create a test user with simple credentials"""
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print("✅ Test user already exists!")
            print(f"   Username: testuser")
            print(f"   Email: {existing_user.email}")
            print(f"   Password: testpass123")
            print(f"\n   If login fails, try resetting password:")
            print(f"   Password hash will be updated...")
            existing_user.password_hash = generate_password_hash('testpass123')
            db.session.commit()
            print(f"   ✓ Password reset complete")
            return
        
        # Check if email already exists with different username
        email_exists = User.query.filter_by(email='test@example.com').first()
        if email_exists:
            print(f"⚠ Email test@example.com already exists with username: {email_exists.username}")
            print(f"   Creating testuser with different email...")
            test_email = 'testuser@example.com'
        else:
            test_email = 'test@example.com'
        
        # Create new test user
        test_user = User(
            username='testuser',
            email=test_email,
            password_hash=generate_password_hash('testpass123'),
            location='Nashville, TN',
            latitude=36.1623,
            longitude=-86.7743
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created successfully!")
        print("")
        print("Login credentials:")
        print("   Username: testuser")
        print("   Password: testpass123")
        print(f"   Email: {test_email}")

if __name__ == '__main__':
    create_test_user()

