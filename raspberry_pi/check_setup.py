#!/usr/bin/env python3
"""
Quick Setup Check for Raspberry Pi

Run this to verify everything is set up correctly.
"""

import sys
import os
from pathlib import Path

print("=" * 60)
print("Raspberry Pi Setup Check")
print("=" * 60)
print()

# Check 1: Python version
print("[1] Checking Python version...")
if sys.version_info < (3, 6):
    print("   ❌ Python 3.6+ required")
    sys.exit(1)
print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# Check 2: Required packages
print("\n[2] Checking required packages...")
missing = []
try:
    import psycopg2
    print("   ✅ psycopg2-binary installed")
except ImportError:
    print("   ❌ psycopg2-binary not installed")
    print("      Install: pip3 install psycopg2-binary")
    missing.append("psycopg2-binary")

try:
    import dotenv
    print("   ✅ python-dotenv installed")
except ImportError:
    print("   ❌ python-dotenv not installed")
    print("      Install: pip3 install python-dotenv")
    missing.append("python-dotenv")

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print("   Run: pip3 install " + " ".join(missing))
    sys.exit(1)

# Check 3: Environment file
print("\n[3] Checking .env file...")
script_dir = Path(__file__).parent
env_file = script_dir / '.env'

if env_file.exists():
    print(f"   ✅ .env file found at {env_file}")
    
    # Check DATABASE_URL
    from dotenv import load_dotenv
    load_dotenv(env_file)
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        print(f"   ✅ DATABASE_URL is set")
        if 'neon.tech' in db_url:
            print("   ✅ Neon database URL detected")
        else:
            print("   ⚠️  DATABASE_URL doesn't look like Neon")
    else:
        print("   ❌ DATABASE_URL not found in .env")
        print("      Add: DATABASE_URL=postgresql://...")
else:
    print(f"   ⚠️  .env file not found at {env_file}")
    print("      Create one with your DATABASE_URL")

# Check 4: Test connection (if DATABASE_URL is set)
db_url = os.environ.get('DATABASE_URL')
if db_url:
    print("\n[4] Testing database connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✅ Connected! {version[:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("      Check your DATABASE_URL in .env file")
else:
    print("\n[4] Skipping connection test (DATABASE_URL not set)")

# Check 5: Scripts exist
print("\n[5] Checking scripts...")
send_script = script_dir / 'send_sensor_data.py'
test_script = script_dir / 'test_connection.py'

if send_script.exists():
    print(f"   ✅ send_sensor_data.py found")
else:
    print(f"   ❌ send_sensor_data.py not found")

if test_script.exists():
    print(f"   ✅ test_connection.py found")
else:
    print(f"   ⚠️  test_connection.py not found")

print("\n" + "=" * 60)
if not missing and db_url:
    print("✅ Setup looks good! You're ready to send sensor data.")
    print("\nNext steps:")
    print("1. Get your Plant ID from Flask app")
    print("2. Update PLANT_ID in .env file")
    print("3. Customize read_sensor_data() in send_sensor_data.py")
    print("4. Test: python3 send_sensor_data.py <plant_id>")
else:
    print("⚠️  Some issues found. Please fix them above.")
print("=" * 60)

