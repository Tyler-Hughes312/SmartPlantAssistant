#!/usr/bin/env python3
"""
Raspberry Pi Sensor Data Sender

This script reads sensor data from your Raspberry Pi and sends it to the Neon Postgres database.
"""

import psycopg2
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import from backend if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # dotenv not required if using system env vars

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    print("   Set it in your .env file or export it:")
    print("   export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'")
    sys.exit(1)


def send_sensor_reading(plant_id, moisture, temperature, light, sensor_id=None):
    """
    Send sensor reading to Neon database.
    
    Args:
        plant_id: ID of the plant (must exist in database)
        moisture: Soil moisture percentage (0-100)
        temperature: Temperature in Fahrenheit
        light: Light level in lux
        sensor_id: Optional sensor identifier
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Insert sensor reading
        cursor.execute("""
            INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (plant_id, float(moisture), float(temperature), float(light), datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Sensor data sent successfully:")
        print(f"   Plant ID: {plant_id}")
        print(f"   Moisture: {moisture}%")
        print(f"   Temperature: {temperature}°F")
        print(f"   Light: {light} lux")
        return True
        
    except psycopg2.IntegrityError as e:
        print(f"❌ Database integrity error: {e}")
        print("   Check that plant_id exists in the database")
        return False
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("   Check your DATABASE_URL and network connection")
        return False
    except Exception as e:
        print(f"❌ Error sending sensor data: {e}")
        import traceback
        traceback.print_exc()
        return False


def read_sensor_data():
    """
    Read sensor data from your Raspberry Pi sensors.
    
    This is a placeholder - replace with your actual sensor reading code.
    For example, if using GPIO:
    
    import RPi.GPIO as GPIO
    import Adafruit_DHT
    
    # Read DHT22 temperature/humidity sensor
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
    
    # Read moisture sensor (analog)
    moisture = read_moisture_sensor()
    
    # Read light sensor
    light = read_light_sensor()
    
    Returns:
        tuple: (moisture, temperature, light) or None if error
    """
    # TODO: Replace with your actual sensor reading code
    # For now, return simulated data
    import random
    return (
        random.uniform(40, 60),  # moisture %
        random.uniform(70, 75),  # temperature °F
        random.uniform(400, 600)  # light lux
    )


def main():
    """Main function to read sensors and send data"""
    print("=" * 60)
    print("Raspberry Pi Sensor Data Sender")
    print("=" * 60)
    
    # Get plant_id from command line or environment
    plant_id = os.environ.get('PLANT_ID')
    if len(sys.argv) > 1:
        plant_id = int(sys.argv[1])
    
    if not plant_id:
        print("❌ ERROR: Plant ID required")
        print("   Usage: python send_sensor_data.py <plant_id>")
        print("   Or set PLANT_ID environment variable")
        sys.exit(1)
    
    plant_id = int(plant_id)
    
    # Read sensor data
    print("\n📡 Reading sensor data...")
    try:
        moisture, temperature, light = read_sensor_data()
        print(f"   Moisture: {moisture:.1f}%")
        print(f"   Temperature: {temperature:.1f}°F")
        print(f"   Light: {light:.1f} lux")
    except Exception as e:
        print(f"❌ Error reading sensors: {e}")
        sys.exit(1)
    
    # Send to database
    print(f"\n📤 Sending data to Neon database (Plant ID: {plant_id})...")
    success = send_sensor_reading(plant_id, moisture, temperature, light)
    
    if success:
        print("\n✅ Success!")
        sys.exit(0)
    else:
        print("\n❌ Failed to send data")
        sys.exit(1)


if __name__ == '__main__':
    main()


