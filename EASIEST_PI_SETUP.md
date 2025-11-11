# EASIEST WAY: Copy-Paste Setup on Raspberry Pi

## Step 1: SSH into Raspberry Pi

```bash
ssh s-plant-pi@10.68.200.197
```

## Step 2: Copy and Paste This Entire Script

Once you're SSH'd into the Pi, copy and paste this entire script:

```bash
#!/bin/bash
WORK_DIR="$HOME/smart_plant_pi"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Install dependencies
pip3 install --user psycopg2-binary python-dotenv || {
    sudo apt update && sudo apt install -y python3-pip
    pip3 install --user psycopg2-binary python-dotenv
}

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
EOF

# Create test_connection.py
cat > test_connection.py << 'PYEOF'
#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set"); exit(1)
print("Testing connection...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"✅ Connected! {cursor.fetchone()[0][:50]}...")
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    print(f"✅ Tables: {cursor.fetchone()[0]}")
    cursor.close()
    conn.close()
    print("✅ All tests passed!")
except Exception as e:
    print(f"❌ Error: {e}"); exit(1)
PYEOF

# Create send_sensor_data.py
cat > send_sensor_data.py << 'PYEOF'
#!/usr/bin/env python3
import psycopg2, os, sys
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')
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
        print(f"✅ Sent: Plant {plant_id}, {moisture:.1f}% moisture, {temperature:.1f}°F, {light:.1f}lux")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
if __name__ == '__main__':
    plant_id = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PLANT_ID', 1))
    moisture, temperature, light = read_sensor_data()
    send_sensor_reading(plant_id, moisture, temperature, light)
PYEOF

chmod +x test_connection.py send_sensor_data.py
echo "✅ Setup complete! Files in: $WORK_DIR"
echo "Test: python3 test_connection.py"
```

## Step 3: Test

```bash
cd ~/smart_plant_pi
python3 test_connection.py
python3 send_sensor_data.py 1  # Replace 1 with your plant ID
```

## Alternative: Download Script

If you can't copy-paste, download the script:

```bash
# On Raspberry Pi
curl -o setup.sh https://raw.githubusercontent.com/YOUR_REPO/raspberry_pi/setup.sh
chmod +x setup.sh
./setup.sh
```

Or create files manually using nano/vi.

