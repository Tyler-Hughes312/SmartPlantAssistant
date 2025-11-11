# Install Hardware Sensor Packages on Raspberry Pi

## Install Required Packages

**On your Raspberry Pi, run:**

```bash
pip3 install --user --break-system-packages \
    adafruit-blinka \
    adafruit-circuitpython-ahtx0 \
    adafruit-circuitpython-bh1750
```

**Or install one at a time:**

```bash
pip3 install --user --break-system-packages adafruit-blinka
pip3 install --user --break-system-packages adafruit-circuitpython-ahtx0
pip3 install --user --break-system-packages adafruit-circuitpython-bh1750
```

## Verify Installation

```bash
python3 -c "import board; import adafruit_ahtx0; import adafruit_bh1750; print('✅ All packages installed!')"
```

## Enable I2C (if not already enabled)

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
# Then reboot: sudo reboot
```

## Verify I2C Devices

After reboot:
```bash
sudo i2cdetect -y 1
```

Should show your sensors:
- AHT20 (usually 0x38)
- BH1750 (usually 0x23)
- Arduino (0x08)

## Then Test the Script

```bash
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

You should see:
```
✅ I2C sensors initialized
Smart Plant Sensor - Real Hardware Sensors
...
```

