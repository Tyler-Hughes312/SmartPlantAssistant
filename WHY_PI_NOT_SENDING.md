# Why Raspberry Pi Hasn't Sent Readings - Diagnostic Steps

## Most Likely Reasons

1. **Haven't run the script yet** - The script needs to be executed manually
2. **Connection error** - Can't connect to Neon database
3. **Missing dependencies** - Python packages not installed
4. **Wrong Plant ID** - Using incorrect plant_id
5. **Script error** - Error when running the script

## Step-by-Step Diagnosis

### Step 1: Check if script exists on Raspberry Pi

**SSH into your Raspberry Pi:**
```bash
ssh s-plant-pi@10.68.200.197
```

**Check if files exist:**
```bash
cd ~/smart_plant_pi
ls -la
```

You should see:
- `send_sensor_data.py`
- `test_connection.py`
- `.env`

### Step 2: Test Database Connection

**On Raspberry Pi:**
```bash
cd ~/smart_plant_pi
python3 test_connection.py
```

**Expected output:**
```
✅ Connected! PostgreSQL 17.5...
✅ Found 3 tables: users, plants, sensor_readings
✅ All tests passed!
```

**If this fails:**
- Check `.env` file has correct DATABASE_URL
- Check internet connection: `ping google.com`
- Check packages installed: `pip3 list | grep psycopg2`

### Step 3: Try Sending Data Manually

**On Raspberry Pi:**
```bash
cd ~/smart_plant_pi
python3 send_sensor_data.py 1
```

**What to look for:**

✅ **Success:**
```
✅ Sensor data sent successfully:
   Plant ID: 1
   Moisture: XX.X%
   Temperature: XX.X°F
   Light: XXX.X lux
```

❌ **Error - Plant not found:**
```
❌ Database integrity error: ...
   Check that plant_id exists in the database
```
**Fix:** Verify Plant ID 1 exists

❌ **Error - Connection failed:**
```
❌ Database connection error: ...
   Check your DATABASE_URL and network connection
```
**Fix:** Check `.env` file and internet connection

❌ **Error - Module not found:**
```
ModuleNotFoundError: No module named 'psycopg2'
```
**Fix:** Install packages:
```bash
pip3 install --user --break-system-packages psycopg2-binary python-dotenv
```

### Step 4: Check for Automation

**If you set up cron/automation, check if it's running:**
```bash
# Check crontab
crontab -l

# Check cron logs
tail -20 ~/sensor_log.txt
```

## Quick Test - Run This Now

**On your Raspberry Pi, run these commands:**

```bash
# 1. Go to directory
cd ~/smart_plant_pi

# 2. Test connection
python3 test_connection.py

# 3. Send test data
python3 send_sensor_data.py 1

# 4. Check if it worked (on your Mac)
# Run this on your Mac:
cd backend
python3 -c "from app import app, db, SensorReading; app.app_context().push(); print(f'Total readings: {SensorReading.query.count()}')"
```

## Common Issues & Fixes

### Issue 1: Script Not Executed
**Problem:** The script needs to be run manually (or via cron)
**Solution:** Run `python3 send_sensor_data.py 1` manually

### Issue 2: .env File Missing
**Problem:** DATABASE_URL not set
**Solution:** Create `.env` file:
```bash
cat > ~/smart_plant_pi/.env << 'EOF'
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
EOF
```

### Issue 3: Packages Not Installed
**Problem:** Missing psycopg2 or python-dotenv
**Solution:**
```bash
pip3 install --user --break-system-packages psycopg2-binary python-dotenv
```

### Issue 4: Wrong Plant ID
**Problem:** Plant ID doesn't exist
**Solution:** Check available plants:
```bash
# On Mac
cd backend
python3 -c "from app import app, db, Plant; app.app_context().push(); [print(f'ID: {p.id}, Name: {p.name}') for p in Plant.query.all()]"
```

## Set Up Automatic Readings

Once manual sending works, set up automation:

```bash
# On Raspberry Pi
crontab -e

# Add this line to run every 5 minutes:
*/5 * * * * cd /home/s-plant-pi/smart_plant_pi && /usr/bin/python3 send_sensor_data.py 1 >> /home/s-plant-pi/sensor_log.txt 2>&1
```

## Summary

The Raspberry Pi **won't send data automatically** until you:
1. ✅ Run the script manually: `python3 send_sensor_data.py 1`
2. ✅ OR set up cron for automatic readings

**Right now:** The script is ready, but it needs to be executed!

