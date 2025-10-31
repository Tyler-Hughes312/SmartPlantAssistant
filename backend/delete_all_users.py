#!/usr/bin/env python3
"""Script to delete all users from the database"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Plant, SensorReading

def delete_all_users():
    """Delete all users and their associated data"""
    with app.app_context():
        try:
            # Get count before deletion
            user_count = User.query.count()
            plant_count = Plant.query.count()
            reading_count = SensorReading.query.count()
            
            print(f"Current database state:")
            print(f"  Users: {user_count}")
            print(f"  Plants: {plant_count}")
            print(f"  Sensor Readings: {reading_count}")
            
            if user_count == 0:
                print("\nNo users to delete.")
                return
            
            # Confirm deletion (skip if --force flag is provided)
            force = '--force' in sys.argv or '-f' in sys.argv
            
            if not force:
                response = input(f"\n⚠️  WARNING: This will delete ALL {user_count} user(s), {plant_count} plant(s), and {reading_count} sensor reading(s).\nContinue? (yes/no): ")
                
                if response.lower() != 'yes':
                    print("Deletion cancelled.")
                    return
            else:
                print(f"\n⚠️  DELETING ALL {user_count} user(s), {plant_count} plant(s), and {reading_count} sensor reading(s)...")
            
            # Delete sensor readings (cascade should handle this, but being explicit)
            SensorReading.query.delete()
            print(f"✓ Deleted {reading_count} sensor reading(s)")
            
            # Delete plants (cascade should handle this, but being explicit)
            Plant.query.delete()
            print(f"✓ Deleted {plant_count} plant(s)")
            
            # Delete users
            User.query.delete()
            print(f"✓ Deleted {user_count} user(s)")
            
            # Commit changes
            db.session.commit()
            
            print("\n✅ All users and associated data deleted successfully!")
            
            # Verify deletion
            remaining_users = User.query.count()
            remaining_plants = Plant.query.count()
            remaining_readings = SensorReading.query.count()
            
            print(f"\nVerification:")
            print(f"  Remaining Users: {remaining_users}")
            print(f"  Remaining Plants: {remaining_plants}")
            print(f"  Remaining Sensor Readings: {remaining_readings}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error deleting users: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    delete_all_users()

