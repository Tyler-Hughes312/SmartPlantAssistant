#!/usr/bin/env python3
"""
Test Neon Postgres Database Connection

Run this script to verify your Neon database connection is working.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
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
    print("\nPlease set DATABASE_URL in your .env file:")
    print("DATABASE_URL=postgresql://user:password@host:port/dbname?sslmode=require")
    sys.exit(1)

print(f"\n📊 Testing database connection...")
print(f"   Database URL: {DATABASE_URL[:50]}...")

# Test 1: Direct psycopg2 connection
print("\n[1] Testing direct psycopg2 connection...")
try:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   ✅ Connected! Postgres version: {version[0][:50]}...")
    cursor.close()
    conn.close()
except ImportError:
    print("   ❌ psycopg2-binary not installed")
    print("   Install with: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Test 2: SQLAlchemy connection
print("\n[2] Testing SQLAlchemy connection...")
try:
    from app import app, db
    with app.app_context():
        # Test connection
        db.engine.connect()
        print(f"   ✅ SQLAlchemy connected!")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"   ✅ Found {len(tables)} tables: {', '.join(tables)}")
        
        # Test query
        from app import User
        user_count = User.query.count()
        print(f"   ✅ Users in database: {user_count}")
        
except Exception as e:
    print(f"   ❌ SQLAlchemy test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Your Neon database is ready to use.")
print("=" * 60)


