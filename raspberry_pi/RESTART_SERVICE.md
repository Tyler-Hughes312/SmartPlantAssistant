# Restart Sensor Service on Raspberry Pi

## On Your Raspberry Pi:

### Step 1: Stop the old service (if running)
```bash
sudo systemctl stop smart-plant-sensor.service
```

### Step 2: Test the script manually first
```bash
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

Let it run for a few readings, then press `Ctrl+C` to stop.

### Step 3: Restart the service
```bash
sudo systemctl restart smart-plant-sensor.service
```

### Step 4: Check status
```bash
sudo systemctl status smart-plant-sensor.service
```

### Step 5: View live logs
```bash
sudo journalctl -u smart-plant-sensor.service -f
```

You should see readings being sent every 10 seconds!

## Quick One-Liner

```bash
sudo systemctl stop smart-plant-sensor.service && \
cd ~/smart_plant_pi && \
sudo systemctl restart smart-plant-sensor.service && \
sleep 2 && \
sudo systemctl status smart-plant-sensor.service
```

## If Using Virtual Environment

If you installed packages in a venv, make sure the service file uses the venv Python path:

```bash
# Check current service file
sudo cat /etc/systemd/system/smart-plant-sensor.service | grep ExecStart

# If it doesn't use venv, update it:
sudo nano /etc/systemd/system/smart-plant-sensor.service
# Change ExecStart to: /home/s-plant-pi/smart_plant_pi/venv/bin/python3
# Then: sudo systemctl daemon-reload
```

