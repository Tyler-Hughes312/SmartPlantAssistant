#!/usr/bin/env python3
"""
Quick Connection Test for Raspberry Pi

Run this to verify your Raspberry Pi can connect to Neon database.
"""

import psycopg2
import os
import sys
from pathlib import Path

# Try to load .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✅ Loaded .env from {env_path}")
    else:
        print(f"⚠️  .env file not found at {env_path}")
        print("   Using system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables")

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("\n❌ ERROR: DATABASE_URL not set")
    print("\nPlease set DATABASE_URL:")
    print("export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'")
    print("\nOr create a .env file with DATABASE_URL")
    sys.exit(1)

print(f"\n📊 Testing Neon database connection...")
print(f"   Database URL: {DATABASE_URL[:50]}...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Test 1: Check version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\n✅ Connected! Postgres version: {version[0][:60]}...")
    
    # Test 2: Check tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"\n✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Test 3: Check if we can insert (test transaction)
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    print(f"\n✅ Users in database: {user_count}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your Raspberry Pi can connect to Neon.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Get your Plant ID from your Flask app")
    print("2. Update PLANT_ID in .env file")
    print("3. Customize read_sensor_data() in send_sensor_data.py")
    print("4. Test: python3 send_sensor_data.py <plant_id>")
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your DATABASE_URL is correct")
    print("2. Verify Raspberry Pi has internet: ping google.com")
    print("3. Check firewall allows outbound connections")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

