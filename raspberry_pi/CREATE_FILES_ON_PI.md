# Create Files Directly on Raspberry Pi

Since SCP isn't working, create the files directly on your Raspberry Pi.

## On Your Raspberry Pi:

### Step 1: Create the Continuous Sensor Script

```bash
cd ~/smart_plant_pi
cat > send_sensor_data_continuous.py << 'PYEOF'
#!/usr/bin/env python3
"""
Continuous Sensor Data Sender - Runs every 10 seconds
Run this script in the background to send sensor data automatically
"""

import psycopg2
import os
import sys
import time
from datetime import datetime
from pathlib import Path

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


def read_sensor_data():
    """Read sensor data - replace with your actual sensor code"""
    import random
    return (
        random.uniform(40, 60),   # moisture %
        random.uniform(70, 75),   # temperature °F
        random.uniform(400, 600)  # light lux
    )


def send_sensor_reading(plant_id, moisture, temperature, light):
    """Send sensor reading to Neon database"""
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
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main loop - sends data every 10 seconds"""
    print("=" * 60)
    print("Smart Plant Sensor - Continuous Mode (10 seconds)")
    print("=" * 60)
    print(f"Plant ID: {PLANT_ID}")
    print(f"Interval: 10 seconds")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    count = 0
    
    try:
        while True:
            count += 1
            
            # Read sensor data
            try:
                moisture, temperature, light = read_sensor_data()
            except Exception as e:
                print(f"❌ Error reading sensors: {e}")
                time.sleep(10)
                continue
            
            # Send to database
            success = send_sensor_reading(PLANT_ID, moisture, temperature, light)
            
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] #{count} ✅ Sent: {moisture:.1f}% moisture, {temperature:.1f}°F, {light:.1f}lux")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] #{count} ❌ Failed to send")
            
            # Wait 10 seconds
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping sensor data collection...")
        print(f"Total readings sent: {count}")
        sys.exit(0)


if __name__ == '__main__':
    main()
PYEOF

chmod +x send_sensor_data_continuous.py
echo "✅ Created send_sensor_data_continuous.py"
```

### Step 2: Create the Setup Script

```bash
cat > setup_10_second_readings.sh << 'SHEOF'
#!/bin/bash
# Setup Automatic Sensor Readings - Every 10 Seconds

set -e

echo "=========================================="
echo "Setting up Automatic Sensor Readings (10 seconds)"
echo "=========================================="
echo ""

WORK_DIR="$HOME/smart_plant_pi"
PLANT_ID="${PLANT_ID:-1}"

# Get Plant ID from .env
if [ -f "$WORK_DIR/.env" ]; then
    ENV_PLANT_ID=$(grep "^PLANT_ID=" "$WORK_DIR/.env" | cut -d'=' -f2)
    if [ ! -z "$ENV_PLANT_ID" ]; then
        PLANT_ID="$ENV_PLANT_ID"
    fi
fi

echo "Plant ID: $PLANT_ID"
echo "Interval: 10 seconds"
echo ""

chmod +x "$WORK_DIR/send_sensor_data_continuous.py"

# Create systemd service
echo "[1/2] Creating systemd service..."
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor Data Collector (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORK_DIR
EnvironmentFile=$WORK_DIR/.env
ExecStart=/usr/bin/python3 $WORK_DIR/send_sensor_data_continuous.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"
echo ""

# Reload systemd
echo "[2/2] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service

echo "✅ Service enabled and started!"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Commands:"
echo "  View logs: sudo journalctl -u smart-plant-sensor.service -f"
echo "  Check status: sudo systemctl status smart-plant-sensor.service"
echo "  Stop: sudo systemctl stop smart-plant-sensor.service"
SHEOF

chmod +x setup_10_second_readings.sh
echo "✅ Created setup_10_second_readings.sh"
```

### Step 3: Run the Setup

```bash
sudo ./setup_10_second_readings.sh
```

### Step 4: Verify It's Working

```bash
sudo systemctl status smart-plant-sensor.service
sudo journalctl -u smart-plant-sensor.service -f
```

## Quick One-Liner (Copy All at Once)

If you want to do it all at once, SSH into your Pi and run:

```bash
cd ~/smart_plant_pi && \
cat > send_sensor_data_continuous.py << 'PYEOF'
#!/usr/bin/env python3
import psycopg2, os, sys, time
from datetime import datetime
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / '.env')
except: pass
DATABASE_URL = os.environ.get('DATABASE_URL')
PLANT_ID = int(os.environ.get('PLANT_ID', 1))
if not DATABASE_URL: print("❌ DATABASE_URL not set"); sys.exit(1)
def read_sensor_data():
    import random
    return random.uniform(40,60), random.uniform(70,75), random.uniform(400,600)
def send_sensor_reading(plant_id, moisture, temperature, light):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp) VALUES (%s, %s, %s, %s, %s)", (plant_id, float(moisture), float(temperature), float(light), datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e: print(f"❌ Error: {e}"); return False
def main():
    print("Smart Plant Sensor - 10 seconds interval")
    print(f"Plant ID: {PLANT_ID}")
    count = 0
    try:
        while True:
            count += 1
            moisture, temperature, light = read_sensor_data()
            success = send_sensor_reading(PLANT_ID, moisture, temperature, light)
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] #{count} ✅ Sent: {moisture:.1f}% moisture")
            time.sleep(10)
    except KeyboardInterrupt:
        print(f"\nStopped. Total: {count}")
        sys.exit(0)
if __name__ == '__main__': main()
PYEOF
chmod +x send_sensor_data_continuous.py && \
cat > setup_10_second_readings.sh << 'SHEOF'
#!/bin/bash
WORK_DIR="$HOME/smart_plant_pi"
PLANT_ID=$(grep "^PLANT_ID=" "$WORK_DIR/.env" 2>/dev/null | cut -d'=' -f2 || echo "1")
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target
[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORK_DIR
EnvironmentFile=$WORK_DIR/.env
ExecStart=/usr/bin/python3 $WORK_DIR/send_sensor_data_continuous.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service
echo "✅ Setup complete! Check: sudo systemctl status smart-plant-sensor.service"
SHEOF
chmod +x setup_10_second_readings.sh && \
echo "✅ Files created! Now run: sudo ./setup_10_second_readings.sh"
```

Then run:
```bash
sudo ./setup_10_second_readings.sh
```

