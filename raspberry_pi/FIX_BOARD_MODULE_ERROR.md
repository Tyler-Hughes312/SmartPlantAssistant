# Fix: module 'board' has no attribute 'SCL'

## Problem

The error means the wrong `board` module is being imported, or Adafruit Blinka isn't installed correctly.

## Solution

### Step 1: Install Adafruit Blinka Properly

```bash
# Remove any conflicting board module
pip3 uninstall board -y 2>/dev/null || true

# Install Adafruit Blinka (the correct one)
sudo pip3 install adafruit-blinka

# Install sensor libraries
sudo pip3 install adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

### Step 2: Verify Installation

```bash
python3 -c "import board; print('SCL:', hasattr(board, 'SCL')); print('SDA:', hasattr(board, 'SDA'))"
```

Should output:
```
SCL: True
SDA: True
```

### Step 3: Enable I2C

```bash
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```

### Step 4: After Reboot, Verify I2C Devices

```bash
sudo i2cdetect -y 1
```

### Step 5: Test Script

```bash
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

### Step 6: Restart Service

```bash
sudo systemctl restart smart-plant-sensor.service
sudo systemctl status smart-plant-sensor.service
```

## Alternative: Use Virtual Environment

If system-wide install doesn't work:

```bash
cd ~/smart_plant_pi
python3 -m venv venv
source venv/bin/activate
pip install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 psycopg2-binary python-dotenv

# Then update service file to use venv Python
sudo nano /etc/systemd/system/smart-plant-sensor.service
# Change ExecStart to: /home/s-plant-pi/smart_plant_pi/venv/bin/python3
sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.service
```

