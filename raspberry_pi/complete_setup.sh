#!/bin/bash
# Complete Raspberry Pi Setup - Copy and paste this entire script on your Pi

set -e

echo "=========================================="
echo "Smart Plant Assistant - Complete Setup"
echo "=========================================="

WORK_DIR="$HOME/smart_plant_pi"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Install dependencies
echo "[1/4] Installing dependencies..."
pip3 install --user psycopg2-binary python-dotenv || {
    echo "Installing pip3..."
    sudo apt update
    sudo apt install -y python3-pip
    pip3 install --user psycopg2-binary python-dotenv
}

# Create .env file
echo "[2/4] Creating .env file..."
cat > .env << 'ENVEOF'
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
ENVEOF

# Create test_connection.py
echo "[3/4] Creating test_connection.py..."
cat > test_connection.py << 'PYEOF'
#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    exit(1)

print("Testing Neon connection...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ Connected! {version[:60]}...")
    
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()
    print(f"✅ Found {len(tables)} tables")
    
    cursor.close()
    conn.close()
    print("✅ All tests passed!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
PYEOF

# Create send_sensor_data.py (simplified version)
echo "[4/4] Creating send_sensor_data.py..."
cat > send_sensor_data.py << 'PYEOF'
#!/usr/bin/env python3
import psycopg2
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

def read_sensor_data():
    """Replace this with your actual sensor reading code"""
    import random
    return (
        random.uniform(40, 60),   # moisture %
        random.uniform(70, 75),   # temperature °F
        random.uniform(400, 600)  # light lux
    )

def send_sensor_reading(plant_id, moisture, temperature, light):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (plant_id, float(moisture), float(temperature), float(light), datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Data sent: Plant {plant_id}, Moisture: {moisture:.1f}%, Temp: {temperature:.1f}°F, Light: {light:.1f}lux")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    plant_id = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PLANT_ID', 1))
    print(f"Reading sensors for Plant ID: {plant_id}...")
    moisture, temperature, light = read_sensor_data()
    print(f"Moisture: {moisture:.1f}%, Temperature: {temperature:.1f}°F, Light: {light:.1f}lux")
    send_sensor_reading(plant_id, moisture, temperature, light)
PYEOF

chmod +x test_connection.py send_sensor_data.py

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test connection: python3 test_connection.py"
echo "2. Get Plant ID from Flask app"
echo "3. Update PLANT_ID in .env: nano .env"
echo "4. Test sensor data: python3 send_sensor_data.py 1"
echo ""
echo "Files created in: $WORK_DIR"

