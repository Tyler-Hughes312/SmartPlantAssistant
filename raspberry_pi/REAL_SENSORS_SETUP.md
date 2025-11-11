# Real Hardware Sensors - Setup Guide

## Hardware Required

- **AHT20**: Temperature & Humidity sensor (I2C)
- **BH1750**: Light sensor (I2C)
- **Arduino**: Soil moisture sensor (I2C slave at address 0x08)

## Installation on Raspberry Pi

```bash
# Install required Python packages
pip3 install --user --break-system-packages \
    psycopg2-binary \
    python-dotenv \
    adafruit-circuitpython-ahtx0 \
    adafruit-circuitpython-bh1750 \
    adafruit-blinka

# Enable I2C on Raspberry Pi
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
# Then reboot: sudo reboot
```

## Hardware Connections

### AHT20 (Temperature & Humidity)
- VCC → 3.3V
- GND → GND
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

### BH1750 (Light Sensor)
- VCC → 3.3V
- GND → GND
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

### Arduino (Soil Moisture)
- Connected via I2C as slave at address 0x08
- SDA → GPIO 2 (SDA)
- SCL → GPIO 3 (SCL)

## Verify I2C Devices

```bash
# Check if sensors are detected
sudo i2cdetect -y 1

# Should show:
# - AHT20 (usually 0x38)
# - BH1750 (usually 0x23)
# - Arduino (0x08)
```

## Schema Mapping

Your sensors → Neon database:
- **soil_moisture** → `moisture` (0-100%)
- **temperature** (Celsius) → `temperature` (converted to Fahrenheit)
- **light** (lux) → `light` (lux)
- **humidity** → Not stored (we use weather API for humidity)

## Usage

```bash
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

## Troubleshooting

### "No module named 'board'"
```bash
pip3 install --user --break-system-packages adafruit-blinka
```

### "I2C not found"
```bash
# Enable I2C
sudo raspi-config
# Or manually:
sudo nano /boot/config.txt
# Add: dtparam=i2c_arm=on
sudo reboot
```

### "Sensor not responding"
- Check wiring connections
- Verify I2C address: `sudo i2cdetect -y 1`
- Check power supply (3.3V)
- Test sensors individually

### "Soil moisture returns None"
- Check Arduino I2C connection
- Verify Arduino is configured as I2C slave at 0x08
- Check Arduino code is running

## Data Flow

```
Physical Sensors → Python Script → Neon Database → Flask Backend → Frontend
  (AHT20, BH1750,    (Read every      (Postgres)     (API)          (Display)
   Arduino)           10 seconds)
```

All real sensor data from your hardware!

