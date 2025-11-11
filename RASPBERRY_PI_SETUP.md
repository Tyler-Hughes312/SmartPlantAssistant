# Raspberry Pi Setup Guide - Connect to Neon Database

This guide will help you connect your Raspberry Pi to your Neon Postgres database.

## Step 1: Install Dependencies on Raspberry Pi

SSH into your Raspberry Pi and install the required packages:

```bash
# Update package list
sudo apt update

# Install Python and pip if not already installed
sudo apt install python3 python3-pip -y

# Install Postgres client library
pip3 install psycopg2-binary python-dotenv
```

## Step 2: Copy Files to Raspberry Pi

You have two options:

### Option A: Clone the Repository on Raspberry Pi

```bash
# On Raspberry Pi
cd ~
git clone <your-repo-url> SmartPlantAssistant
cd SmartPlantAssistant
```

### Option B: Copy Files via SCP (from your Mac)

```bash
# From your Mac, copy the raspberry_pi folder
scp -r raspberry_pi/ pi@raspberry-pi-ip:~/
scp .env pi@raspberry-pi-ip:~/raspberry_pi/.env
```

## Step 3: Set Up Environment Variables

On your Raspberry Pi, create or edit the `.env` file:

```bash
cd ~/raspberry_pi  # or wherever you put the files
nano .env
```

Add this content (use YOUR connection string from your Mac's .env file):

```bash
# Neon Database Connection String
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Your Plant ID (get this from your Flask app after creating a plant)
PLANT_ID=1
```

**Important**: Use the same `DATABASE_URL` from your Mac's `.env` file!

## Step 4: Test the Connection

Test that your Raspberry Pi can connect to Neon:

```bash
cd ~/raspberry_pi
python3 send_sensor_data.py 1
```

You should see:
```
✅ Sensor data sent successfully:
   Plant ID: 1
   Moisture: XX%
   Temperature: XX°F
   Light: XX lux
```

## Step 5: Customize Sensor Reading Function

Edit `send_sensor_data.py` and replace the `read_sensor_data()` function with your actual sensor code.

### Example for DHT22 Temperature/Humidity Sensor:

```python
import Adafruit_DHT

def read_sensor_data():
    # DHT22 sensor on GPIO pin 4
    sensor = Adafruit_DHT.DHT22
    pin = 4
    
    humidity, temperature_c = Adafruit_DHT.read_retry(sensor, pin)
    
    if temperature_c is None:
        temperature_c = 22.0  # Default if sensor fails
    
    # Convert to Fahrenheit
    temperature = (temperature_c * 9/5) + 32
    
    # Read moisture sensor (replace with your code)
    moisture = read_moisture_sensor()  # Your function here
    
    # Read light sensor (replace with your code)
    light = read_light_sensor()  # Your function here
    
    return moisture, temperature, light
```

### Example for Analog Moisture Sensor:

```python
import RPi.GPIO as GPIO
import time

def read_moisture_sensor():
    # Configure GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)  # Power pin
    
    # Power on sensor
    GPIO.output(18, GPIO.HIGH)
    time.sleep(0.1)
    
    # Read analog value (using MCP3008 ADC or similar)
    # This is pseudocode - adjust for your hardware
    adc_value = read_adc(0)  # Channel 0
    
    # Convert to percentage (0-100%)
    moisture = (adc_value / 1023.0) * 100
    
    GPIO.output(18, GPIO.LOW)
    GPIO.cleanup()
    
    return moisture
```

## Step 6: Set Up Automated Readings

### Option A: Using Cron (Simple)

Edit crontab:
```bash
crontab -e
```

Add this line to run every 5 minutes:
```bash
*/5 * * * * cd /home/pi/raspberry_pi && /usr/bin/python3 send_sensor_data.py 1 >> /home/pi/sensor_log.txt 2>&1
```

### Option B: Using Systemd Timer (Recommended)

Create service file:
```bash
sudo nano /etc/systemd/system/smart-plant-sensor.service
```

Add:
```ini
[Unit]
Description=Smart Plant Sensor Data Collector
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/raspberry_pi
EnvironmentFile=/home/pi/raspberry_pi/.env
ExecStart=/usr/bin/python3 /home/pi/raspberry_pi/send_sensor_data.py 1
StandardOutput=journal
StandardError=journal
```

Create timer file:
```bash
sudo nano /etc/systemd/system/smart-plant-sensor.timer
```

Add:
```ini
[Unit]
Description=Run Smart Plant Sensor every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable smart-plant-sensor.timer
sudo systemctl start smart-plant-sensor.timer
sudo systemctl status smart-plant-sensor.timer
```

## Step 7: Get Your Plant ID

Before sending data, you need to create a plant in your Flask app and get its ID:

1. Start your Flask backend on your Mac
2. Register/login to your app
3. Create a plant (note the plant ID)
4. Use that ID in your Raspberry Pi script

Or check existing plants:
```bash
# On your Mac, in backend directory
python3 -c "from app import app, db, Plant; app.app_context().push(); plants = Plant.query.all(); [print(f'ID: {p.id}, Name: {p.name}') for p in plants]"
```

## Troubleshooting

### "Connection refused" or "Network unreachable"
- Check your Raspberry Pi has internet: `ping google.com`
- Verify firewall allows outbound connections
- Test connection: `python3 -c "import psycopg2; conn = psycopg2.connect('your-connection-string'); print('Connected!')"`

### "Plant not found" error
- Make sure the plant_id exists in your database
- Check plant exists: Use the query above to list plants

### "Permission denied"
- Make script executable: `chmod +x send_sensor_data.py`
- Check file permissions: `ls -la send_sensor_data.py`

### Sensor reading errors
- Test sensors individually before integrating
- Add error handling in `read_sensor_data()` function
- Use try/except blocks

## Quick Test Script

Create a simple test file `test_connection.py`:

```python
#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connected! Postgres version: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run: `python3 test_connection.py`

## Next Steps

1. ✅ Test connection from Raspberry Pi
2. ✅ Customize sensor reading code
3. ✅ Set up automated readings (cron or systemd)
4. ✅ Monitor data in your Flask app dashboard
5. ✅ Check Neon dashboard for database activity

Your Raspberry Pi sensor data will now appear in your Flask app dashboard!

