# Raspberry Pi Sensor Integration

This directory contains scripts for connecting your Raspberry Pi sensors (AHT20, BH1750, Arduino I2C soil moisture) to the Smart Plant Assistant Neon Postgres database.

## Hardware Setup

### Supported Sensors

- **AHT20**: Temperature and humidity sensor (I2C)
- **BH1750**: Light sensor (I2C)
- **Arduino I2C Soil Moisture Sensor**: Soil moisture sensor (I2C slave at address 0x08)

### I2C Setup

1. Enable I2C on Raspberry Pi:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

2. Verify I2C is enabled:
   ```bash
   sudo i2cdetect -y 1
   # You should see devices at their I2C addresses
   ```

## Software Setup

### 1. Install Dependencies

```bash
pip3 install --user --break-system-packages \
  psycopg2-binary \
  python-dotenv \
  adafruit-blinka \
  adafruit-circuitpython-ahtx0 \
  adafruit-circuitpython-bh1750 \
  RPi.GPIO
```

**Note**: If you're using a virtual environment, activate it first:
```bash
source venv/bin/activate
pip install psycopg2-binary python-dotenv adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 RPi.GPIO
```

### 2. Configure Environment Variables

Create a `.env` file in your home directory or project directory:

```bash
nano ~/.env
```

Add:
```bash
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
```

**Important**: Replace `PLANT_ID=1` with your actual plant ID from the database.

### 3. Set Up Automatic Sensor Readings

The project includes a systemd service that reads sensors every 10 seconds and sends data to Neon.

**Setup:**
```bash
cd raspberry_pi
chmod +x setup_10_second_readings.sh
sudo ./setup_10_second_readings.sh
```

This script:
- Creates a systemd service file
- Configures it to run every 10 seconds
- Sets up environment variables
- Enables and starts the service

### 4. Verify Service Status

```bash
# Check service status
sudo systemctl status smart-plant-sensor.service

# View recent logs
sudo journalctl -u smart-plant-sensor.service -f

# Restart service if needed
sudo systemctl restart smart-plant-sensor.service
```

## Manual Testing

To test sensor reading manually:

```bash
cd raspberry_pi
python3 send_sensor_data_continuous.py
```

This will read sensors once and print the results. Press Ctrl+C to stop.

## Troubleshooting

### "ModuleNotFoundError: No module named 'board'"

This means `adafruit-blinka` is not installed correctly. Try:

```bash
pip3 install --user --break-system-packages --force-reinstall adafruit-blinka RPi.GPIO
```

If using a virtual environment:
```bash
source venv/bin/activate
pip install --force-reinstall adafruit-blinka RPi.GPIO
```

### "module 'board' has no attribute 'SCL'"

This indicates `adafruit-blinka` is not detecting your Raspberry Pi correctly. Verify:

```bash
python3 -c "import board; print('SCL:', hasattr(board, 'SCL')); print('SDA:', hasattr(board, 'SDA'))"
```

Should output:
```
SCL: True
SDA: True
```

If not, reinstall:
```bash
pip3 install --user --break-system-packages --force-reinstall adafruit-blinka
```

### Service Fails to Start

1. Check logs:
   ```bash
   sudo journalctl -u smart-plant-sensor.service -n 50
   ```

2. Verify paths in service file:
   ```bash
   sudo cat /etc/systemd/system/smart-plant-sensor.service
   ```

3. Ensure script has correct permissions:
   ```bash
   ls -la send_sensor_data_continuous.py
   chmod +x send_sensor_data_continuous.py
   ```

### No Sensor Data in Database

1. Verify service is running:
   ```bash
   sudo systemctl status smart-plant-sensor.service
   ```

2. Check database connection:
   ```bash
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('DATABASE_URL:', 'SET' if os.getenv('DATABASE_URL') else 'NOT SET')"
   ```

3. Verify plant ID exists:
   - Check your database for the plant ID
   - Ensure `PLANT_ID` in service matches your database

### I2C Connection Issues

1. Verify I2C is enabled:
   ```bash
   lsmod | grep i2c
   ```

2. Check for devices:
   ```bash
   sudo i2cdetect -y 1
   ```

3. Verify sensor connections:
   - AHT20: SDA → GPIO 2, SCL → GPIO 3, VCC → 3.3V, GND → GND
   - BH1750: SDA → GPIO 2, SCL → GPIO 3, VCC → 3.3V, GND → GND
   - Arduino: Connected via I2C at address 0x08

## Service Management

### Stop Service
```bash
sudo systemctl stop smart-plant-sensor.service
```

### Disable Service (prevent auto-start)
```bash
sudo systemctl disable smart-plant-sensor.service
```

### Restart Service
```bash
sudo systemctl restart smart-plant-sensor.service
```

### View Live Logs
```bash
sudo journalctl -u smart-plant-sensor.service -f
```

## Files

- `send_sensor_data_continuous.py`: Main script that reads sensors and sends to database
- `setup_10_second_readings.sh`: Setup script for systemd service

## Customization

To change the reading interval, edit `/etc/systemd/system/smart-plant-sensor.service`:

```ini
[Service]
# Change OnUnitActiveSec to desired interval (e.g., 30s, 1min, 5min)
OnUnitActiveSec=10s
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.service
```
