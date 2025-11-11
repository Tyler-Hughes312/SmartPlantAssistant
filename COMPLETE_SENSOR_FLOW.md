# Complete Guide: Raspberry Pi → Database → Frontend

## Complete Flow

```
Raspberry Pi → Neon Database → Flask Backend → React Frontend
```

## Step 1: Send Data from Raspberry Pi to Database

### On Your Raspberry Pi:

1. **Make sure `.env` file is set up:**
   ```bash
   cd ~/smart_plant_pi
   cat .env
   ```
   
   Should show:
   ```bash
   DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   PLANT_ID=1
   ```

2. **Test sending sensor data:**
   ```bash
   python3 send_sensor_data.py 1
   ```
   
   You should see:
   ```
   ✅ Sensor data sent successfully:
      Plant ID: 1
      Moisture: XX.X%
      Temperature: XX.X°F
      Light: XXX.X lux
   ```

3. **Customize sensor reading (when you have real sensors):**
   
   Edit `send_sensor_data.py` and replace the `read_sensor_data()` function (around line 85) with your actual sensor code.

4. **Set up automated readings (optional):**
   
   Add to crontab to run every 5 minutes:
   ```bash
   crontab -e
   ```
   
   Add this line:
   ```
   */5 * * * * cd /home/s-plant-pi/smart_plant_pi && /usr/bin/python3 send_sensor_data.py 1 >> /home/s-plant-pi/sensor_log.txt 2>&1
   ```

## Step 2: Verify Data in Database

### On Your Mac:

Check if data was inserted:
```bash
cd backend
python3 -c "
from app import app, db, SensorReading
app.app_context().push()
readings = SensorReading.query.order_by(SensorReading.timestamp.desc()).limit(5).all()
for r in readings:
    print(f'{r.timestamp}: Plant {r.plant_id} - Moisture: {r.moisture}%, Temp: {r.temperature}°F, Light: {r.light}lux')
"
```

## Step 3: Frontend Automatically Displays Data

The frontend **automatically** fetches and displays sensor data:

1. **Frontend polls every 5 seconds** - The Dashboard component automatically refreshes sensor data
2. **Data appears in:**
   - **Sensor Dashboard** - Shows current moisture, temperature, light
   - **Sensor Chart** - Historical trends over time
   - **Plant Health Score** - Calculated from sensor data
   - **Watering Prediction** - Uses sensor data for ML predictions

### How It Works:

1. **Dashboard loads** → Calls `fetchSensorData(plantId)` 
2. **Backend API** → `/api/sensor-data?plant_id=1` reads from Neon database
3. **Data displayed** → Shows in SensorDashboard component
4. **Auto-refresh** → Updates every 5 seconds

## Step 4: View Data in Frontend

1. **Make sure backend is running:**
   ```bash
   cd backend
   python3 app.py
   ```

2. **Make sure frontend is running:**
   ```bash
   cd frontend
   npm start
   ```

3. **Open browser:**
   ```
   http://localhost:3001
   ```

4. **Login:**
   - Username: `testuser`
   - Password: `testpass123`

5. **View sensor data:**
   - Select "Test Plant" from the plant dropdown
   - Sensor readings appear automatically
   - Data refreshes every 5 seconds

## Troubleshooting

### Data not appearing in frontend?

1. **Check if data exists in database:**
   ```bash
   cd backend
   python3 -c "from app import app, db, SensorReading; app.app_context().push(); print(f'Total readings: {SensorReading.query.count()}')"
   ```

2. **Check backend logs:**
   - Look at the terminal where `python3 app.py` is running
   - Check for any errors when fetching sensor data

3. **Check browser console:**
   - Press F12 → Console tab
   - Look for API errors

4. **Verify plant ID matches:**
   - Make sure Raspberry Pi is using the same Plant ID as your plant in the app
   - Check: `SELECT id, name FROM plants;`

### Data not sending from Raspberry Pi?

1. **Test connection:**
   ```bash
   python3 test_connection.py
   ```

2. **Check DATABASE_URL:**
   ```bash
   cat .env | grep DATABASE_URL
   ```

3. **Verify Plant ID exists:**
   - Make sure Plant ID 1 exists in database
   - Or update PLANT_ID in `.env` to match your plant

## Quick Test Flow

1. **On Raspberry Pi:**
   ```bash
   cd ~/smart_plant_pi
   python3 send_sensor_data.py 1
   ```

2. **On Mac - Check database:**
   ```bash
   cd backend
   python3 -c "from app import app, db, SensorReading; app.app_context().push(); r = SensorReading.query.order_by(SensorReading.timestamp.desc()).first(); print(f'Latest: {r.moisture}% moisture, {r.temperature}°F, {r.light}lux')"
   ```

3. **In Browser:**
   - Refresh `http://localhost:3001`
   - Data should appear within 5 seconds

## Summary

✅ **Raspberry Pi** → Sends data directly to Neon database  
✅ **Database** → Stores sensor readings  
✅ **Backend API** → Reads from database  
✅ **Frontend** → Automatically fetches and displays every 5 seconds  

**No manual steps needed!** Once data is in the database, the frontend will automatically show it.

