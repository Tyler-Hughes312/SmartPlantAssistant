#!/usr/bin/env python3
"""Script to register a new user via API"""

import requests
import json
import sys

API_URL = "http://localhost:5001/api/register"

def register_user():
    """Register a new user"""
    if len(sys.argv) < 4:
        print("Usage: python register_user.py <username> <email> <password>")
        print("\nExample:")
        print("  python register_user.py myuser myuser@example.com mypassword123")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    try:
        response = requests.post(
            API_URL,
            json={
                'username': username,
                'email': email,
                'password': password
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("✅ User registered successfully!")
            print(f"   Username: {data['user']['username']}")
            print(f"   Email: {data['user']['email']}")
        else:
            error = response.json().get('error', 'Unknown error')
            print(f"❌ Registration failed: {error}")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server.")
        print("   Make sure the backend is running on http://localhost:5001")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    register_user()

