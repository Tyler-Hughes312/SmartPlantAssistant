# Update send_sensor_data_continuous.py on Raspberry Pi

## Option 1: Copy-Paste Directly on Raspberry Pi (Easiest)

**SSH into your Raspberry Pi:**
```bash
ssh s-plant-pi@10.68.200.197
```

**Then run this command to update the file:**

```bash
cd ~/smart_plant_pi && cat > send_sensor_data_continuous.py << 'PYEOF'
#!/usr/bin/env python3
"""
Continuous Sensor Data Sender - Real Hardware Sensors
Reads from AHT20, BH1750, and Arduino I2C sensors
Sends data to Neon Postgres database every 10 seconds
"""

import psycopg2
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Hardware sensor imports
import board
import busio
import adafruit_ahtx0
import adafruit_bh1750

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL')
PLANT_ID = int(os.environ.get('PLANT_ID', 1))

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

# --------------------------
# I2C Setup
# --------------------------
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Digital sensors
    aht20 = adafruit_ahtx0.AHTx0(i2c)
    bh1750 = adafruit_bh1750.BH1750(i2c)
    
    # Arduino I2C slave for soil moisture
    ARDUINO_ADDR = 0x08
    
    print("✅ I2C sensors initialized")
except Exception as e:
    print(f"❌ Error initializing sensors: {e}")
    print("   Make sure sensors are connected and I2C is enabled")
    sys.exit(1)


def read_soil_moisture():
    """Read soil moisture from Arduino I2C slave."""
    try:
        while not i2c.try_lock():
            pass
        try:
            result = bytearray(2)
            i2c.readfrom_into(ARDUINO_ADDR, result)
            raw = (result[0] << 8) | result[1]
            soil_percent = ((650 - raw) / 650) * 100
            # Clamp to 0-100 range
            return max(0, min(100, soil_percent))
        finally:
            i2c.unlock()
    except Exception as e:
        print(f"⚠️  Error reading soil moisture: {e}")
        return None


def read_sensor_data():
    """
    Read sensor data from physical hardware.
    
    Returns:
        tuple: (moisture, temperature, light) or None if error
    """
    try:
        # Read from AHT20 (temperature and humidity)
        temperature_c = aht20.temperature
        humidity = aht20.relative_humidity
        
        # Convert temperature to Fahrenheit (our schema uses Fahrenheit)
        temperature_f = (temperature_c * 9/5) + 32
        
        # Read from BH1750 (light sensor)
        light = bh1750.lux
        
        # Read from Arduino I2C (soil moisture)
        soil_moisture = read_soil_moisture()
        
        # If soil moisture read failed, use None (will be handled by backend)
        if soil_moisture is None:
            print("⚠️  Soil moisture sensor not responding, using None")
        
        return (
            soil_moisture,  # moisture % (0-100) or None
            temperature_f,  # temperature in Fahrenheit
            light           # light in lux
        )
    except Exception as e:
        print(f"❌ Error reading sensors: {e}")
        return None


def send_sensor_reading(plant_id, moisture, temperature, light):
    """
    Send sensor reading to Neon Postgres database.
    
    Args:
        plant_id: ID of the plant (must exist in database)
        moisture: Soil moisture percentage (0-100) or None
        temperature: Temperature in Fahrenheit
        light: Light level in lux
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Insert sensor reading
        # Note: moisture can be None if sensor fails
        cursor.execute("""
            INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            plant_id,
            float(moisture) if moisture is not None else None,
            float(temperature),
            float(light),
            datetime.now()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
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


def main():
    """Main loop - reads sensors and sends data every 10 seconds"""
    print("=" * 60)
    print("Smart Plant Sensor - Real Hardware Sensors")
    print("=" * 60)
    print(f"Plant ID: {PLANT_ID}")
    print(f"Interval: 10 seconds")
    print("Sensors:")
    print("  - AHT20: Temperature & Humidity")
    print("  - BH1750: Light")
    print("  - Arduino I2C: Soil Moisture")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    count = 0
    error_count = 0
    
    try:
        while True:
            count += 1
            
            # Read sensor data
            sensor_result = read_sensor_data()
            
            if sensor_result is None:
                error_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] #{count} ❌ Failed to read sensors")
                time.sleep(10)
                continue
            
            moisture, temperature, light = sensor_result
            
            # Send to Neon database
            success = send_sensor_reading(PLANT_ID, moisture, temperature, light)
            
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                moisture_str = f"{moisture:.1f}%" if moisture is not None else "N/A"
                print(f"[{timestamp}] #{count} ✅ Sent: {moisture_str} moisture, {temperature:.1f}°F, {light:.1f}lux")
                error_count = 0  # Reset error count on success
            else:
                error_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] #{count} ❌ Failed to send to database")
            
            # If too many errors, warn user
            if error_count >= 5:
                print(f"⚠️  Warning: {error_count} consecutive errors. Check sensor connections and database.")
            
            # Wait 10 seconds
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping sensor data collection...")
        print(f"Total readings sent: {count}")
        print(f"Errors encountered: {error_count}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
PYEOF

chmod +x send_sensor_data_continuous.py
echo "✅ File updated!"
```

## Option 2: Try SCP Again (From Your Mac)

```bash
scp raspberry_pi/send_sensor_data_continuous.py s-plant-pi@10.68.200.197:~/smart_plant_pi/
```

## After Updating

1. **Stop the old service** (if running):
   ```bash
   sudo systemctl stop smart-plant-sensor.service
   ```

2. **Test the new script**:
   ```bash
   cd ~/smart_plant_pi
   python3 send_sensor_data_continuous.py
   ```

3. **If it works, restart the service**:
   ```bash
   sudo systemctl restart smart-plant-sensor.service
   sudo systemctl status smart-plant-sensor.service
   ```

The file is ready with your real hardware sensor code!

