# Data Sources - Real vs Simulated

## Current Status:

### ✅ REAL DATA:
1. **Weather Data**: 
   - Source: National Weather Service (NWS) API
   - Real-time weather from your location
   - Temperature, humidity, precipitation, wind speed, forecast

2. **User Accounts & Plants**: 
   - Stored in SQLite database (`backend/smart_plant.db`)
   - Real user registration, login, plant management

3. **Stored Sensor Readings**: 
   - If you POST sensor data via API, it's stored in the database
   - Real historical data once posted

### ⚠️ SIMULATED/TEST DATA:
1. **Sensor Data (Default)**: 
   - Currently using **simulated sensor readings** when no real data exists
   - The app checks for real readings first, but generates fake data if none found
   - Simulated values:
     - Light: 300-500 lux (varies by time of day)
     - Moisture: 43-47% (slowly decreasing)
     - Temperature: 70-74°F (varies by time of day)

## How It Works:

### When you first add a plant:
- No sensor readings exist yet
- App generates simulated data to show something
- This allows you to see the interface working

### When real sensor data is posted:
- Use the `/api/sensor-data` POST endpoint
- Real readings are stored in the database
- Real data will be used for health scores and predictions

## To Connect Real Sensors:

### Option 1: POST sensor data via API
```bash
curl -X POST http://localhost:5001/api/sensor-data \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "plant_id": 1,
    "light": 450,
    "moisture": 52,
    "temperature": 73
  }'
```

### Option 2: Modify `get_sensor_data()` function
In `backend/app.py`, replace the simulated data generation with your sensor API calls.

### Option 3: Sensor device integration
Have your sensor device POST to `/api/sensor-data` endpoint periodically.

## Summary:

| Data Type | Status | Source |
|-----------|--------|--------|
| Weather | ✅ Real | NWS API |
| Users/Plants | ✅ Real | SQLite Database |
| Sensor Data | ⚠️ Simulated | Generated when no real data |
| Health Scores | ⚠️ Based on simulated data | Calculated from sensor readings |
| Predictions | ⚠️ Based on simulated data | ML model using sensor + weather |

**Bottom line**: Weather is real, but sensor data is simulated until you connect real sensors or post real readings via the API.

