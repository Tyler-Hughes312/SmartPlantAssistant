# What is the Setup Script and How to Run It

## What is the Setup Script?

The `setup_10_second_readings.sh` script is a **bash script** that automatically configures your Raspberry Pi to send sensor readings every 10 seconds.

### What it does:

1. ✅ Checks that all required files exist
2. ✅ Reads your Plant ID from `.env` file
3. ✅ Creates a systemd service (runs in background)
4. ✅ Configures it to start automatically on boot
5. ✅ Starts the service immediately
6. ✅ Shows you how to monitor and control it

## How to Run It

### Step 1: Copy Files to Raspberry Pi

**First, make sure the files are on your Raspberry Pi:**

**Option A: If files are already there**
```bash
ssh s-plant-pi@10.68.200.197
cd ~/smart_plant_pi
ls -la
```

You should see:
- `send_sensor_data_continuous.py`
- `setup_10_second_readings.sh`
- `.env`
- `test_connection.py`

**Option B: Copy files from your Mac**

If files aren't on the Pi yet, copy them:

```bash
# From your Mac
scp raspberry_pi/send_sensor_data_continuous.py s-plant-pi@10.68.200.197:~/smart_plant_pi/
scp raspberry_pi/setup_10_second_readings.sh s-plant-pi@10.68.200.197:~/smart_plant_pi/
```

### Step 2: SSH into Raspberry Pi

```bash
ssh s-plant-pi@10.68.200.197
```

### Step 3: Navigate to Directory

```bash
cd ~/smart_plant_pi
```

### Step 4: Make Script Executable

```bash
chmod +x setup_10_second_readings.sh
```

### Step 5: Run the Setup Script

```bash
./setup_10_second_readings.sh
```

**Or with sudo if needed:**
```bash
sudo ./setup_10_second_readings.sh
```

## What You'll See

The script will output something like:

```
==========================================
Setting up Automatic Sensor Readings (10 seconds)
==========================================

Plant ID: 1
Interval: 10 seconds

[1/2] Creating systemd service...
✅ Service file created

[2/2] Enabling and starting service...
✅ Service enabled and started!

Service status:
● smart-plant-sensor.service - Smart Plant Sensor Data Collector (10 seconds)
   Loaded: loaded (/etc/systemd/system/smart-plant-sensor.service)
   Active: active (running) since ...
   
==========================================
✅ Setup Complete!
==========================================
```

## Verify It's Working

### Check if service is running:

```bash
sudo systemctl status smart-plant-sensor.service
```

### View live logs (see readings being sent):

```bash
sudo journalctl -u smart-plant-sensor.service -f
```

You should see output every 10 seconds:
```
[2025-11-10 17:30:00] #1 ✅ Sent: 45.2% moisture, 72.5°F, 550.3lux
[2025-11-10 17:30:10] #2 ✅ Sent: 46.1% moisture, 73.1°F, 545.8lux
```

### Check database (on your Mac):

```bash
cd backend
python3 -c "
from app import app, db, SensorReading
app.app_context().push()
count = SensorReading.query.count()
print(f'Total readings: {count}')
latest = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(5).all()
for r in latest:
    print(f'{r.timestamp}: {r.moisture}% moisture')
"
```

## Troubleshooting

### "Permission denied" error?

```bash
chmod +x setup_10_second_readings.sh
sudo ./setup_10_second_readings.sh
```

### "File not found" error?

Make sure you're in the right directory:
```bash
cd ~/smart_plant_pi
ls -la setup_10_second_readings.sh
```

### Service not starting?

Check logs:
```bash
sudo journalctl -u smart-plant-sensor.service -n 50
```

### Want to stop it?

```bash
sudo systemctl stop smart-plant-sensor.service
```

### Want to start it again?

```bash
sudo systemctl start smart-plant-sensor.service
```

## Quick Copy-Paste Commands

**Run these commands in order on your Raspberry Pi:**

```bash
# 1. SSH into Pi (from your Mac)
ssh s-plant-pi@10.68.200.197

# 2. Go to directory
cd ~/smart_plant_pi

# 3. Make script executable
chmod +x setup_10_second_readings.sh

# 4. Run setup script
sudo ./setup_10_second_readings.sh

# 5. Check it's working
sudo systemctl status smart-plant-sensor.service

# 6. View live logs
sudo journalctl -u smart-plant-sensor.service -f
```

## Summary

**Setup Script:** `setup_10_second_readings.sh`  
**What it does:** Configures automatic sensor readings every 10 seconds  
**How to run:** `sudo ./setup_10_second_readings.sh`  
**Where:** On your Raspberry Pi in `~/smart_plant_pi/` directory  

Once you run it, your Raspberry Pi will automatically send sensor data every 10 seconds!

