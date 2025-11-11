# Step-by-Step Raspberry Pi Setup - After SSH

## ✅ Yes, it's already set up for the sensor_readings table!

The `sensor_readings` table exists in Neon with these columns:
- `id` (primary key)
- `plant_id` (foreign key to plants table)
- `moisture` (float)
- `temperature` (float)
- `light` (float)
- `timestamp` (datetime)

## Complete Step-by-Step Instructions

### Step 1: SSH into Raspberry Pi
```bash
ssh s-plant-pi@10.68.200.197
```

### Step 2: Navigate to the directory
```bash
cd ~/smart_plant_pi
```

### Step 3: Install Python packages (fix the error)
```bash
pip3 install --user --break-system-packages psycopg2-binary python-dotenv
```

### Step 4: Verify .env file exists and has correct connection string
```bash
cat .env
```

You should see:
```
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
```

### Step 5: Test database connection
```bash
python3 test_connection.py
```

Expected output:
```
✅ Connected! PostgreSQL 17.5...
✅ Found 3 tables: users, plants, sensor_readings
✅ All tests passed!
```

### Step 6: Get your Plant ID from Neon database

**On your Mac**, run this to get Plant IDs:
```bash
cd backend
python3 -c "from app import app, db, Plant; app.app_context().push(); plants = Plant.query.all(); [print(f'ID: {p.id}, Name: {p.name}, Sensor ID: {p.sensor_id}') for p in plants]"
```

Or create a plant first:
1. Start Flask: `cd backend && python3 app.py`
2. Open browser: `http://localhost:3000`
3. Register/Login
4. Create a plant (note the Plant ID)

### Step 7: Update Plant ID in .env file
```bash
nano .env
```

Change `PLANT_ID=1` to your actual plant ID, then save (Ctrl+X, Y, Enter)

### Step 8: Test sending sensor data
```bash
python3 send_sensor_data.py 1
```

Replace `1` with your actual Plant ID. You should see:
```
✅ Sent: Plant 1, XX.X% moisture, XX.X°F, XXX.Xlux
```

### Step 9: Verify data in Neon database

**On your Mac**, check if data was inserted:
```bash
cd backend
python3 -c "from app import app, db, SensorReading; app.app_context().push(); readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(5).all(); [print(f'{r.timestamp}: Plant {r.plant_id} - Moisture: {r.moisture}%, Temp: {r.temperature}°F, Light: {r.light}lux') for r in readings]"
```

### Step 10: Customize sensor reading function (Optional)

Edit the `read_sensor_data()` function in `send_sensor_data.py`:
```bash
nano send_sensor_data.py
```

Find the `read_sensor_data()` function (around line 85) and replace with your actual sensor code.

### Step 11: Set up automated readings (Optional)

**Option A: Using Cron (every 5 minutes)**
```bash
crontab -e
```

Add this line (replace `1` with your Plant ID):
```
*/5 * * * * cd /home/s-plant-pi/smart_plant_pi && /usr/bin/python3 send_sensor_data.py 1 >> /home/s-plant-pi/sensor_log.txt 2>&1
```

**Option B: Using Systemd Timer**
```bash
sudo nano /etc/systemd/system/smart-plant-sensor.service
```

Paste:
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

Create timer:
```bash
sudo nano /etc/systemd/system/smart-plant-sensor.timer
```

Paste:
```ini
[Unit]
Description=Run Smart Plant Sensor every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable smart-plant-sensor.timer
sudo systemctl start smart-plant-sensor.timer
sudo systemctl status smart-plant-sensor.timer
```

## Quick Reference Commands

```bash
# Test connection
python3 test_connection.py

# Send sensor data manually
python3 send_sensor_data.py <plant_id>

# Check recent sensor readings (on Mac)
cd backend && python3 -c "from app import app, db, SensorReading; app.app_context().push(); readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(5).all(); [print(f'{r.timestamp}: Plant {r.plant_id} - {r.moisture}% moisture, {r.temperature}°F, {r.light}lux') for r in readings]"

# View cron logs
tail -f ~/sensor_log.txt

# Check systemd timer status
sudo systemctl status smart-plant-sensor.timer
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'psycopg2'"**
```bash
export PATH="$HOME/.local/bin:$PATH"
python3 test_connection.py
```

**"Plant not found" error**
- Make sure Plant ID exists in database
- Check: Get Plant IDs using the command in Step 6
- Update PLANT_ID in .env file

**"Connection refused"**
- Check internet: `ping google.com`
- Verify DATABASE_URL in .env matches your Mac's .env
- Test: `python3 test_connection.py`

## ✅ Verification Checklist

- [ ] Packages installed (`psycopg2-binary`, `python-dotenv`)
- [ ] `.env` file has correct DATABASE_URL
- [ ] Connection test passes (`python3 test_connection.py`)
- [ ] Plant ID obtained and updated in .env
- [ ] Sensor data sending works (`python3 send_sensor_data.py <plant_id>`)
- [ ] Data appears in Flask app dashboard
- [ ] Automated readings set up (optional)

Your Raspberry Pi is now ready to send sensor data to Neon!

