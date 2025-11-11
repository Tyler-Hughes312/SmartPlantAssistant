# Fix: board module import error

## Problem
The `board` module from Adafruit Blinka isn't importing correctly.

## Solution

### Step 1: Check What's Installed

```bash
pip3 list | grep -i adafruit
pip3 list | grep -i board
```

### Step 2: Check Python Path

```bash
python3 -c "import sys; print('\n'.join(sys.path))"
```

### Step 3: Try Installing with --user flag

```bash
pip3 install --user --upgrade adafruit-blinka
```

### Step 4: Verify Installation Location

```bash
python3 -c "import adafruit_blinka; print(adafruit_blinka.__file__)"
```

### Step 5: Check if board module exists

```bash
python3 -c "import pkgutil; print([m.name for m in pkgutil.iter_modules() if 'board' in m.name.lower()])"
```

### Step 6: Try Direct Import Test

```bash
python3 << EOF
try:
    import adafruit_blinka.board.raspberrypi.raspi_40pin as board
    print("✅ Found board via adafruit_blinka")
    print("SCL:", hasattr(board, 'SCL'))
    print("SDA:", hasattr(board, 'SDA'))
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF
```

### Step 7: Install All Required Packages Together

```bash
sudo pip3 install --upgrade --force-reinstall \
    adafruit-blinka \
    adafruit-circuitpython-ahtx0 \
    adafruit-circuitpython-bh1750 \
    RPi.GPIO \
    rpi-ws281x
```

### Step 8: Alternative - Use Virtual Environment

If system-wide install doesn't work:

```bash
cd ~/smart_plant_pi
python3 -m venv venv
source venv/bin/activate
pip install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 psycopg2-binary python-dotenv

# Test in venv
python -c "import board; print('SCL:', hasattr(board, 'SCL')); print('SDA:', hasattr(board, 'SDA'))"

# Update service file to use venv Python
sudo nano /etc/systemd/system/smart-plant-sensor.service
# Change ExecStart to: /home/s-plant-pi/smart_plant_pi/venv/bin/python3
sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.service
```

### Step 9: Check I2C is Enabled

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Then reboot: sudo reboot
```

### Step 10: After Reboot, Check I2C Devices

```bash
sudo i2cdetect -y 1
```

You should see device addresses (like 0x38 for AHT20, 0x23 for BH1750).

