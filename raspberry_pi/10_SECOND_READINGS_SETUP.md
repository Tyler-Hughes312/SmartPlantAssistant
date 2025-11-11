# Setup Automatic Readings Every 10 Seconds

## Quick Setup

**On your Raspberry Pi:**

1. **Copy the files** (if not already there):
   ```bash
   # Make sure send_sensor_data_continuous.py is in ~/smart_plant_pi/
   ```

2. **Run the setup script:**
   ```bash
   cd ~/smart_plant_pi
   chmod +x setup_10_second_readings.sh
   ./setup_10_second_readings.sh
   ```

This will:
- ✅ Create a systemd service
- ✅ Start sending data every 10 seconds
- ✅ Auto-restart if it crashes
- ✅ Run on boot automatically

## Manual Setup (Alternative)

### Option 1: Run in Background Manually

```bash
cd ~/smart_plant_pi
nohup python3 send_sensor_data_continuous.py > sensor_output.log 2>&1 &
```

### Option 2: Use screen/tmux

```bash
# Install screen if needed
sudo apt install screen -y

# Start screen session
screen -S sensor

# Run the script
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r sensor
```

## Verify It's Working

### Check Service Status

```bash
sudo systemctl status smart-plant-sensor.service
```

### View Live Logs

```bash
sudo journalctl -u smart-plant-sensor.service -f
```

### Check Database (on your Mac)

```bash
cd backend
python3 -c "
from app import app, db, SensorReading
app.app_context().push()
count = SensorReading.query.count()
print(f'Total readings: {count}')
if count > 0:
    latest = SensorReading.query.order_by(SensorReading.timestamp.desc()).first()
    print(f'Latest: {latest.timestamp} - {latest.moisture}% moisture')
"
```

You should see new readings appearing every 10 seconds!

## Stop/Start/Restart

```bash
# Stop
sudo systemctl stop smart-plant-sensor.service

# Start
sudo systemctl start smart-plant-sensor.service

# Restart
sudo systemctl restart smart-plant-sensor.service

# Disable (won't start on boot)
sudo systemctl disable smart-plant-sensor.service

# Enable (will start on boot)
sudo systemctl enable smart-plant-sensor.service
```

## Change Interval

To change from 10 seconds to a different interval:

1. **Edit the script:**
   ```bash
   nano ~/smart_plant_pi/send_sensor_data_continuous.py
   ```

2. **Change this line** (around line 80):
   ```python
   time.sleep(10)  # Change 10 to your desired seconds
   ```

3. **Restart the service:**
   ```bash
   sudo systemctl restart smart-plant-sensor.service
   ```

## Troubleshooting

### Service not starting?

```bash
# Check logs
sudo journalctl -u smart-plant-sensor.service -n 50

# Check if Python script works manually
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

### No data appearing?

1. **Check service is running:**
   ```bash
   sudo systemctl status smart-plant-sensor.service
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u smart-plant-sensor.service -f
   ```

3. **Test connection:**
   ```bash
   python3 test_connection.py
   ```

## Summary

✅ **Setup:** Run `setup_10_second_readings.sh`  
✅ **Interval:** 10 seconds  
✅ **Auto-start:** Enabled on boot  
✅ **Monitoring:** `sudo journalctl -u smart-plant-sensor.service -f`  

Your Raspberry Pi will now send sensor data every 10 seconds automatically!

