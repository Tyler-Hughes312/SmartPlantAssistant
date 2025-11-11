# Raspberry Pi Sensor Integration

This directory contains scripts for connecting your Raspberry Pi sensors to the Smart Plant Assistant database.

## Setup

1. **Install dependencies on Raspberry Pi**:
   ```bash
   pip3 install psycopg2-binary python-dotenv
   ```

2. **Configure environment variables**:
   ```bash
   # Copy .env.example to .env and fill in your Neon database URL
   cp .env.example .env
   nano .env
   ```

3. **Set your plant ID**:
   ```bash
   export PLANT_ID=1  # Replace with your actual plant ID
   ```

## Usage

### Manual Sensor Reading

```bash
python3 send_sensor_data.py <plant_id>
```

### Automated Sensor Reading (Cron)

Add to crontab to run every 5 minutes:
```bash
crontab -e

# Add this line:
*/5 * * * * cd /path/to/raspberry_pi && /usr/bin/python3 send_sensor_data.py 1 >> /var/log/sensor_data.log 2>&1
```

### Systemd Service (Recommended)

Create `/etc/systemd/system/smart-plant-sensor.service`:

```ini
[Unit]
Description=Smart Plant Sensor Data Collector
After=network.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/path/to/raspberry_pi
Environment="PLANT_ID=1"
EnvironmentFile=/path/to/raspberry_pi/.env
ExecStart=/usr/bin/python3 /path/to/raspberry_pi/send_sensor_data.py 1
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then create a timer `/etc/systemd/system/smart-plant-sensor.timer`:

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
```

## Customizing Sensor Reading

Edit the `read_sensor_data()` function in `send_sensor_data.py` to match your hardware:

- **DHT22/DHT11** (Temperature/Humidity): Use `Adafruit_DHT` library
- **Moisture Sensor**: Read analog pin or use capacitive sensor
- **Light Sensor**: Use photoresistor or BH1750 sensor

Example for DHT22:
```python
import Adafruit_DHT

def read_sensor_data():
    sensor = Adafruit_DHT.DHT22
    pin = 4  # GPIO pin number
    
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    # Convert to Fahrenheit
    temperature = (temperature * 9/5) + 32 if temperature else 72
    
    # Read other sensors...
    moisture = read_moisture()
    light = read_light()
    
    return moisture, temperature, light
```

## Troubleshooting

- **Connection errors**: Check your DATABASE_URL and network connection
- **Plant not found**: Ensure the plant_id exists in your database
- **Permission errors**: Make sure the script has execute permissions (`chmod +x`)


