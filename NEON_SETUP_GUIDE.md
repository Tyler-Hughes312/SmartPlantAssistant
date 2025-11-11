# Neon Postgres Database Setup Guide

This guide will help you connect your Smart Plant Assistant to Neon Postgres database, allowing your Raspberry Pi and Flask backend to share the same database.

## What is Neon?

Neon is a serverless Postgres database service that provides:
- Automatic scaling
- Serverless architecture (pay for what you use)
- Free tier available
- Easy connection from anywhere (Raspberry Pi, local machine, cloud)

## Step 1: Create a Neon Account and Database

1. Go to [neon.tech](https://neon.tech) and sign up for a free account
2. Create a new project
3. Note your connection string (it will look like):
   ```
   postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

## Step 2: Configure Your Flask Backend

1. **Add DATABASE_URL to your `.env` file** (in project root):
   ```bash
   DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

2. **Install Postgres dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   
   This will install `psycopg2-binary` which is required for Postgres connections.

3. **Initialize the database**:
   ```bash
   python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
   ```

## Step 3: Connect from Raspberry Pi

### Option A: Using Python (Recommended)

1. **Install dependencies on Raspberry Pi**:
   ```bash
   pip3 install psycopg2-binary
   ```

2. **Create a script to send sensor data** (`raspberry_pi/send_sensor_data.py`):
   ```python
   import psycopg2
   import os
   from datetime import datetime
   from dotenv import load_dotenv
   
   # Load environment variables
   load_dotenv()
   
   DATABASE_URL = os.environ.get('DATABASE_URL')
   
   def send_sensor_reading(plant_id, moisture, temperature, light):
       """Send sensor reading to Neon database"""
       try:
           conn = psycopg2.connect(DATABASE_URL)
           cursor = conn.cursor()
           
           # Insert sensor reading
           cursor.execute("""
               INSERT INTO sensor_readings (plant_id, moisture, temperature, light, timestamp)
               VALUES (%s, %s, %s, %s, %s)
           """, (plant_id, moisture, temperature, light, datetime.now()))
           
           conn.commit()
           cursor.close()
           conn.close()
           print(f"✅ Sensor data sent: moisture={moisture}%, temp={temperature}°F, light={light}lux")
           return True
       except Exception as e:
           print(f"❌ Error sending sensor data: {e}")
           return False
   
   if __name__ == '__main__':
       # Example usage
       send_sensor_reading(
           plant_id=1,
           moisture=45.5,
           temperature=72.3,
           light=520
       )
   ```

3. **Set up environment variable on Raspberry Pi**:
   ```bash
   # Add to ~/.bashrc or create ~/.env file
   export DATABASE_URL="postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/dbname?sslmode=require"
   ```

### Option B: Using HTTP API (Alternative)

Instead of direct database access, your Raspberry Pi can send data via HTTP to your Flask backend:

```python
import requests
import json

def send_sensor_data_via_api(plant_id, moisture, temperature, light, api_url="http://your-backend-url:5001"):
    """Send sensor data via Flask API"""
    try:
        response = requests.post(
            f"{api_url}/api/sensor-data",
            json={
                'plant_id': plant_id,
                'moisture': moisture,
                'temperature': temperature,
                'light': light
            },
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print("✅ Sensor data sent successfully")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
```

## Step 4: Verify Connection

### Test Flask Backend Connection:

```bash
cd backend
python3 -c "
from app import app, db
with app.app_context():
    from app import User
    user_count = User.query.count()
    print(f'✅ Database connected! Users in database: {user_count}')
"
```

### Test Raspberry Pi Connection:

```bash
python3 raspberry_pi/send_sensor_data.py
```

## Step 5: Migrate Existing Data (Optional)

If you have existing SQLite data, you can migrate it:

```bash
# Export from SQLite
sqlite3 smart_plant.db .dump > backup.sql

# Import to Neon (using psql or pgAdmin)
# Note: You'll need to convert SQLite syntax to Postgres syntax
```

## Troubleshooting

### Connection Issues

1. **SSL Required**: Neon requires SSL. Make sure your connection string includes `?sslmode=require`
2. **Firewall**: Ensure your Raspberry Pi can reach `*.neon.tech` domains
3. **Credentials**: Double-check your username, password, and database name

### Common Errors

- **"SSL connection required"**: Add `?sslmode=require` to your connection string
- **"Connection refused"**: Check your Neon project is active and connection string is correct
- **"Table does not exist"**: Run `db.create_all()` to create tables

### Testing Connection

```python
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ Connected to Postgres: {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Security Best Practices

1. **Never commit your `.env` file** - It's already in `.gitignore`
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate passwords** - Change your Neon password periodically
4. **Use connection pooling** - For production, consider using a connection pooler

## Next Steps

1. Set up your Raspberry Pi sensor reading script
2. Configure automatic sensor data collection (cron job or systemd service)
3. Monitor your Neon dashboard for database usage
4. Set up database backups (Neon provides automatic backups)

## Resources

- [Neon Documentation](https://neon.tech/docs)
- [Postgres Python Driver (psycopg2)](https://www.psycopg.org/docs/)
- [SQLAlchemy Postgres Guide](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)


