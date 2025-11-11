#!/usr/bin/env python3
"""Quick test of prediction API"""
import sys
sys.path.insert(0, '/Users/tylerhughes/Projects/SmartPlantAssistant/backend')

from app import app
import json

with app.test_client() as client:
    # Login
    login_resp = client.post('/api/login', json={'username': 'test', 'password': 'test'})
    print("Login status:", login_resp.status_code)
    
    # Test weather-only prediction
    resp = client.post('/api/predict', json={
        'sensor': {},
        'weather': {'temperature': 75, 'humidity': 50, 'precipitation': 0}
    })
    print("\nWeather-only response:")
    print(json.dumps(resp.get_json(), indent=2))
    
    # Test with moisture
    resp2 = client.post('/api/predict', json={
        'sensor': {'moisture': 45, 'temperature': 72},
        'weather': {'temperature': 75, 'humidity': 50, 'precipitation': 0}
    })
    print("\nWith moisture response:")
    print(json.dumps(resp2.get_json(), indent=2))

