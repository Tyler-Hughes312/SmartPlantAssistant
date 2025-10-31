#!/usr/bin/env python3
"""Reset test user password to ensure it's correct"""

from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    
    if user:
        # Reset password
        user.password_hash = generate_password_hash('testpass123')
        db.session.commit()
        
        print("✅ Test user password reset!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: testpass123")
    else:
        print("❌ Test user not found!")
        print("   Creating new test user...")
        
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass123'),
            location='Nashville, TN',
            latitude=36.1623,
            longitude=-86.7743
        )
        db.session.add(user)
        db.session.commit()
        
        print("✅ Test user created!")
        print(f"   Username: testuser")
        print(f"   Password: testpass123")

