# Why No Sensor Readings? - Troubleshooting Guide

## Current Status

✅ **Plant exists**: Test Plant (ID: 1)  
❌ **No sensor readings**: 0 readings in database

## Why No Readings?

The Raspberry Pi script hasn't sent any data yet. This could be because:

1. **Haven't run the script yet** - Need to execute `send_sensor_data.py`
2. **Connection issue** - Raspberry Pi can't connect to Neon
3. **Wrong Plant ID** - Using incorrect plant_id
4. **Script error** - Error when running the script

## Test Sending Data

### Option 1: Test from Your Mac (Quick Test)

I just created a test reading from your Mac to verify the database works. Check if it appears:

```bash
cd backend
python3 -c "
from app import app, db, SensorReading
app.app_context().push()
readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(3).all()
for r in readings:
    print(f'{r.timestamp}: Plant {r.plant_id} - {r.moisture}% moisture, {r.temperature}°F, {r.light}lux')
"
```

### Option 2: Test from Raspberry Pi

**On your Raspberry Pi:**

1. **Test connection first:**
   ```bash
   cd ~/smart_plant_pi
   python3 test_connection.py
   ```

2. **Send test data:**
   ```bash
   python3 send_sensor_data.py 1
   ```

3. **Check for errors:**
   - If you see "✅ Sensor data sent successfully" → Data is in database!
   - If you see an error → Check the error message

## Common Issues

### Issue 1: "Plant not found" Error

**Solution:** Make sure Plant ID 1 exists:
```bash
# On Mac
cd backend
python3 -c "from app import app, db, Plant; app.app_context().push(); print([(p.id, p.name) for p in Plant.query.all()])"
```

### Issue 2: Connection Error

**Solution:** Check DATABASE_URL on Raspberry Pi:
```bash
# On Raspberry Pi
cat ~/smart_plant_pi/.env | grep DATABASE_URL
```

Should match your Mac's `.env` file exactly.

### Issue 3: Module Not Found

**Solution:** Install packages on Raspberry Pi:
```bash
pip3 install --user --break-system-packages psycopg2-binary python-dotenv
```

## Verify Data Was Sent

**On your Mac, check database:**
```bash
cd backend
python3 -c "
from app import app, db, SensorReading
app.app_context().push()
count = SensorReading.query.count()
print(f'Total readings: {count}')
if count > 0:
    latest = SensorReading.query.order_by(SensorReading.timestamp.desc()).first()
    print(f'Latest: {latest.moisture}% moisture, {latest.temperature}°F, {latest.light}lux')
"
```

## Next Steps

1. ✅ **Test from Mac** - I just created a test reading
2. **Check frontend** - Refresh `http://localhost:3001` - data should appear
3. **Test from Raspberry Pi** - Run `send_sensor_data.py 1`
4. **Set up automation** - Add to crontab for automatic readings

The database is working - you just need to send data from the Raspberry Pi!

