# Setup Automatic Sensor Readings - Quick Guide

## Option 1: Use the Setup Script (Easiest)

**On your Raspberry Pi:**

```bash
cd ~/smart_plant_pi

# Download or copy the setup script
# Then run:
chmod +x setup_automatic_readings.sh
./setup_automatic_readings.sh
```

This will:
- ✅ Set up cron job to run every 5 minutes
- ✅ Test the connection
- ✅ Create log file for monitoring

## Option 2: Manual Setup with Cron

**On your Raspberry Pi:**

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add this line** (replace `1` with your Plant ID if different):
   ```bash
   */5 * * * * cd /home/s-plant-pi/smart_plant_pi && /usr/bin/python3 send_sensor_data.py 1 >> /home/s-plant-pi/sensor_log.txt 2>&1
   ```

3. **Save and exit** (Ctrl+X, Y, Enter)

4. **Verify it was added:**
   ```bash
   crontab -l
   ```

## Option 3: Systemd Timer (More Advanced)

Create a systemd service and timer for better control.

### Create Service File

```bash
sudo nano /etc/systemd/system/smart-plant-sensor.service
```

Add:
```ini
[Unit]
Description=Smart Plant Sensor Data Collector
After=network.target

[Service]
Type=oneshot
User=s-plant-pi
WorkingDirectory=/home/s-plant-pi/smart_plant_pi
EnvironmentFile=/home/s-plant-pi/smart_plant_pi/.env
ExecStart=/usr/bin/python3 /home/s-plant-pi/smart_plant_pi/send_sensor_data.py 1
StandardOutput=journal
StandardError=journal
```

### Create Timer File

```bash
sudo nano /etc/systemd/system/smart-plant-sensor.timer
```

Add:
```ini
[Unit]
Description=Run Smart Plant Sensor every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

### Enable and Start

```bash
sudo systemctl enable smart-plant-sensor.timer
sudo systemctl start smart-plant-sensor.timer
sudo systemctl status smart-plant-sensor.timer
```

## Verify It's Working

### Check Cron Logs

```bash
tail -f ~/sensor_log.txt
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

### Check Frontend

- Open `http://localhost:3001`
- Data should appear automatically
- New readings every 5 minutes

## Change Reading Interval

### For Cron:

```bash
crontab -e
```

Change `*/5` to:
- `*/1` - Every 1 minute
- `*/10` - Every 10 minutes
- `*/30` - Every 30 minutes
- `0 * * * *` - Every hour

### For Systemd Timer:

Edit `/etc/systemd/system/smart-plant-sensor.timer` and change:
```ini
OnUnitActiveSec=5min
```

To:
- `1min` - Every 1 minute
- `10min` - Every 10 minutes
- `30min` - Every 30 minutes
- `1h` - Every hour

Then restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.timer
```

## Troubleshooting

### Cron job not running?

1. **Check cron service:**
   ```bash
   sudo systemctl status cron
   ```

2. **Check cron logs:**
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. **Test manually:**
   ```bash
   cd ~/smart_plant_pi
   python3 send_sensor_data.py 1
   ```

### No data appearing?

1. **Check log file:**
   ```bash
   tail -20 ~/sensor_log.txt
   ```

2. **Check database connection:**
   ```bash
   python3 test_connection.py
   ```

3. **Verify Plant ID:**
   ```bash
   cat ~/smart_plant_pi/.env | grep PLANT_ID
   ```

## Summary

✅ **Easiest:** Use `setup_automatic_readings.sh` script  
✅ **Manual:** Edit crontab with `crontab -e`  
✅ **Advanced:** Use systemd timer  

Once set up, readings will be sent automatically every 5 minutes!

