# Complete Code: How Data is Read at Each Stage

## 1. Raspberry Pi: Reading Sensors & Writing to Neon

**File:** `raspberry_pi/send_sensor_data_continuous.py`

```python
def read_sensor_data():
    """Read sensor data - replace with your actual sensor code"""
    import random
    return (
        random.uniform(40, 60),   # moisture %
        random.uniform(70, 75),   # temperature °F
        random.uniform(400, 600)  # light lux
    )

def send_sensor_reading(plant_id, moisture, temperature, light):
    """Send sensor reading to Neon database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (plant_id, float(moisture), float(temperature), float(light), datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main loop - sends data every 10 seconds"""
    count = 0
    while True:
        count += 1
        # Read sensor data
        moisture, temperature, light = read_sensor_data()
        # Send to Neon database
        success = send_sensor_reading(PLANT_ID, moisture, temperature, light)
        time.sleep(10)  # Wait 10 seconds
```

**Note:** Replace `read_sensor_data()` with your actual sensor reading code (GPIO, I2C, etc.)

---

## 2. Backend: Reading from Neon Database

**File:** `backend/app.py`

### Get Latest Sensor Reading

```python
@app.route('/api/sensor-data', methods=['GET'])
@login_required
def get_sensor_data():
    """Get current sensor data for user's plants"""
    plant_id = request.args.get('plant_id', type=int)
    
    if plant_id:
        # Get specific plant's data
        plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
        if not plant:
            return jsonify({'error': 'Plant not found'}), 404
        
        # Get latest reading from Neon database
        latest_reading = SensorReading.query.filter_by(plant_id=plant_id)\
            .order_by(SensorReading.timestamp.desc()).first()
        
        if latest_reading:
            return jsonify({
                'plant_id': plant_id,
                'plant_name': plant.name,
                'light': latest_reading.light,
                'moisture': latest_reading.moisture,
                'temperature': latest_reading.temperature,
                'timestamp': latest_reading.timestamp.isoformat(),
                'is_simulated': False  # Real sensor data from Neon
            })
        else:
            # No readings yet
            return jsonify({
                'plant_id': plant_id,
                'plant_name': plant.name,
                'light': None,
                'moisture': None,
                'temperature': None,
                'timestamp': None,
                'is_simulated': False,
                'message': 'No sensor readings available yet.'
            })
```

### Get Sensor History

```python
@app.route('/api/sensor-data/history', methods=['GET'])
@login_required
def get_sensor_history():
    """Get sensor reading history"""
    plant_id = request.args.get('plant_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not plant_id:
        return jsonify({'error': 'plant_id required'}), 400
    
    plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404
    
    # Read history from Neon database
    readings = SensorReading.query.filter_by(plant_id=plant_id)\
        .order_by(SensorReading.timestamp.desc())\
        .limit(limit).all()
    
    return jsonify([{
        'id': r.id,
        'plant_id': r.plant_id,
        'moisture': r.moisture,
        'temperature': r.temperature,
        'light': r.light,
        'timestamp': r.timestamp.isoformat()
    } for r in readings])
```

---

## 3. Frontend: Reading from Backend API

**File:** `frontend/src/services/api.js`

```javascript
// Sensor Data API calls
export const fetchSensorData = async (plantId = null) => {
  const params = plantId ? { plant_id: plantId } : {};
  const response = await api.get('/sensor-data', { params });
  return response.data;
};

export const getSensorHistory = async (plantId, limit = 20) => {
  const response = await api.get('/sensor-data/history', {
    params: { plant_id: plantId, limit }
  });
  return response.data;
};
```

**File:** `frontend/src/components/Dashboard.js`

```javascript
const loadData = async () => {
  if (!selectedPlantId) return;

  try {
    setError(null);
    // Fetch both current sensor data and history in parallel
    const [sensor, historyData] = await Promise.all([
      fetchSensorData(selectedPlantId),      // GET /api/sensor-data?plant_id=1
      getSensorHistory(selectedPlantId, 20)  // GET /api/sensor-data/history?plant_id=1&limit=20
    ]);

    setSensorData(sensor);
    setHistory(historyData.map(h => ({
      ...h,
      timestamp: new Date(h.timestamp),
    })));

    // Auto-refresh every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  } catch (err) {
    console.error('Error loading data:', err);
    setError(err.response?.data?.error || err.message);
  }
};
```

**File:** `frontend/src/components/SensorDashboard.js`

```javascript
const SensorDashboard = ({ sensorData }) => {
  // Only show real data from Neon database
  if (!sensorData || sensorData.is_simulated) {
    return <div>Waiting for sensor data from Raspberry Pi...</div>;
  }

  // Check if we have real values
  const hasRealData = sensorData.light != null && 
                      sensorData.moisture != null && 
                      sensorData.temperature != null;

  if (!hasRealData) {
    return <div>Waiting for sensor data from Raspberry Pi...</div>;
  }

  // Display real data
  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-value">{Math.round(sensorData.light)} lux</div>
        <div className="card-label">Light (from Raspberry Pi)</div>
      </div>
      <div className="card">
        <div className="card-value">{Math.round(sensorData.moisture)}%</div>
        <div className="card-label">Moisture (from Raspberry Pi)</div>
      </div>
      <div className="card">
        <div className="card-value">{Math.round(sensorData.temperature)}°F</div>
        <div className="card-label">Temperature (from Raspberry Pi)</div>
      </div>
    </div>
  );
};
```

---

## Complete Data Flow

```
┌─────────────────┐
│  Raspberry Pi   │
│                 │
│ 1. Read Sensors │
│    - Moisture   │
│    - Temp       │
│    - Light      │
└────────┬────────┘
         │
         │ INSERT INTO sensor_readings
         ▼
┌─────────────────┐
│  Neon Database   │
│                 │
│  Stores:        │
│  - plant_id     │
│  - moisture     │
│  - temperature  │
│  - light        │
│  - timestamp    │
└────────┬────────┘
         │
         │ SELECT FROM sensor_readings
         ▼
┌─────────────────┐
│ Flask Backend    │
│                 │
│ GET /api/       │
│ sensor-data     │
│                 │
│ Reads from Neon │
└────────┬────────┘
         │
         │ HTTP GET request
         ▼
┌─────────────────┐
│ React Frontend   │
│                 │
│ fetchSensorData │
│                 │
│ Displays data   │
└─────────────────┘
```

---

## Key Code Locations

1. **Raspberry Pi Reading:** `raspberry_pi/send_sensor_data_continuous.py` - Line 31-38
2. **Raspberry Pi Writing:** `raspberry_pi/send_sensor_data_continuous.py` - Line 41-56
3. **Backend Reading Latest:** `backend/app.py` - Line 536-574
4. **Backend Reading History:** `backend/app.py` - Line 654-680
5. **Frontend API Calls:** `frontend/src/services/api.js` - Line 60-76
6. **Frontend Display:** `frontend/src/components/Dashboard.js` - Line 78-154
7. **Frontend Component:** `frontend/src/components/SensorDashboard.js` - Line 4-78

All data flows through Neon database - no test/simulated data!

