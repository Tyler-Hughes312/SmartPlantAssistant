#!/usr/bin/env python3
"""Migration script to add location, latitude and longitude columns to users table"""

import sqlite3
import os

def migrate_database():
    db_paths = [
        'smart_plant.db',
        'instance/smart_plant.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("No database file found. It will be created with the new schema on next run.")
        return
    
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'location' not in columns:
            print("Adding location column...")
            cursor.execute("ALTER TABLE users ADD COLUMN location VARCHAR(200) DEFAULT 'New York, NY'")
            # Update existing users with coordinates to have a location string (if lat/lon exist)
            if 'latitude' in columns and 'longitude' in columns:
                try:
                    cursor.execute("UPDATE users SET location = CAST(latitude AS TEXT) || ', ' || CAST(longitude AS TEXT) WHERE location IS NULL OR location = 'New York, NY'")
                except:
                    pass  # Ignore if update fails
        
        if 'latitude' not in columns:
            print("Adding latitude column...")
            cursor.execute("ALTER TABLE users ADD COLUMN latitude REAL DEFAULT 40.7128")
        
        if 'longitude' not in columns:
            print("Adding longitude column...")
            cursor.execute("ALTER TABLE users ADD COLUMN longitude REAL DEFAULT -74.0060")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()

