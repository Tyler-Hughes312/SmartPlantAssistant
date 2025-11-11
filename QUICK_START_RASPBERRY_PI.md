# Quick Start Guide - Raspberry Pi to Neon Connection

## 🚀 Automated Setup (Easiest Way)

### On Your Raspberry Pi:

1. **Copy files to Raspberry Pi** (from your Mac):
   ```bash
   # Replace with your Pi's IP address
   scp -r raspberry_pi/ pi@192.168.1.XXX:~/
   ```

2. **SSH into Raspberry Pi**:
   ```bash
   ssh pi@192.168.1.XXX
   ```

3. **Run the automated setup script**:
   ```bash
   cd ~/raspberry_pi
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Edit .env file** (use your actual connection string):
   ```bash
   nano ~/smart_plant_pi/.env
   ```
   
   Make sure DATABASE_URL matches your Mac's .env file:
   ```bash
   DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   PLANT_ID=1
   ```

5. **Check setup**:
   ```bash
   cd ~/smart_plant_pi
   python3 check_setup.py
   ```

6. **Test connection**:
   ```bash
   python3 test_connection.py
   ```

7. **Get Plant ID** (on your Mac):
   ```bash
   cd backend
   python3 -c "from app import app, db, Plant; app.app_context().push(); plants = Plant.query.all(); [print(f'ID: {p.id}, Name: {p.name}') for p in plants]"
   ```

8. **Update Plant ID in .env** (on Raspberry Pi):
   ```bash
   nano ~/smart_plant_pi/.env
   # Change PLANT_ID to match your plant
   ```

9. **Test sending sensor data**:
   ```bash
   cd ~/smart_plant_pi
   python3 send_sensor_data.py 1  # Replace 1 with your plant ID
   ```

## 📋 Manual Setup (If automated doesn't work)

### Step 1: Install Dependencies
```bash
pip3 install psycopg2-binary python-dotenv
```

### Step 2: Create Directory
```bash
mkdir -p ~/smart_plant_pi
cd ~/smart_plant_pi
```

### Step 3: Copy Files
Copy these files from your Mac to `~/smart_plant_pi/`:
- `send_sensor_data.py`
- `test_connection.py`
- `.env` (create this with your DATABASE_URL)

### Step 4: Create .env File
```bash
nano ~/smart_plant_pi/.env
```

Add:
```bash
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
```

### Step 5: Test
```bash
cd ~/smart_plant_pi
python3 test_connection.py
python3 send_sensor_data.py 1
```

## 🔧 Your Connection String

**Use your connection string from your Neon project** (format):

```
postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## ✅ Verification Checklist

- [ ] Dependencies installed (`psycopg2-binary`, `python-dotenv`)
- [ ] `.env` file created with DATABASE_URL
- [ ] Connection test passes (`python3 test_connection.py`)
- [ ] Plant ID obtained from Flask app
- [ ] PLANT_ID updated in .env file
- [ ] Sensor data sending works (`python3 send_sensor_data.py <plant_id>`)

## 🎯 Next Steps After Setup

1. **Customize sensor reading**: Edit `read_sensor_data()` in `send_sensor_data.py`
2. **Set up automation**: Use cron or systemd (see RASPBERRY_PI_SETUP.md)
3. **Monitor data**: Check your Flask app dashboard to see sensor readings

## 🆘 Troubleshooting

**Connection fails?**
- Check internet: `ping google.com`
- Verify DATABASE_URL in .env matches your Mac's .env
- Test: `python3 test_connection.py`

**Plant not found?**
- Get Plant ID: See step 7 above
- Update PLANT_ID in .env file
- Make sure plant exists in Neon database

**Permission errors?**
- Make scripts executable: `chmod +x *.py`
- Check file ownership: `ls -la`

For detailed troubleshooting, see `RASPBERRY_PI_SETUP.md`

