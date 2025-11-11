# Install Sensor Packages - Alternative Methods

## Method 1: Install System-Wide (Recommended)

```bash
sudo pip3 install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

## Method 2: Use apt (if available)

```bash
sudo apt update
sudo apt install python3-pip python3-dev python3-smbus i2c-tools
sudo pip3 install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

## Method 3: Create Virtual Environment

```bash
cd ~/smart_plant_pi
python3 -m venv venv
source venv/bin/activate
pip install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 psycopg2-binary python-dotenv
```

Then update the script to use the venv Python:
```bash
# Update service to use: /home/s-plant-pi/smart_plant_pi/venv/bin/python3
```

## Method 4: Install with --break-system-packages (if Python 3.11+)

```bash
pip3 install --break-system-packages adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

## Check Python Version

```bash
python3 --version
```

If it's Python 3.11+, you need `--break-system-packages` flag.

## Troubleshooting

### "externally-managed-environment" error
```bash
sudo pip3 install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

### "Permission denied"
```bash
sudo pip3 install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
```

### Check if packages are already installed
```bash
pip3 list | grep adafruit
```

If they're installed but Python can't find them, you might need to use the full path or check PYTHONPATH.

