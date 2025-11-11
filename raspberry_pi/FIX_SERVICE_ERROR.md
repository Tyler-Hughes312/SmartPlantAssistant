# Fix Service Startup Error

The service is failing to start. Let's check the logs and fix it.

## Check the Error Logs

**On your Raspberry Pi, run:**

```bash
sudo journalctl -xeu smart-plant-sensor.service -n 50
```

This will show the actual error message.

## Common Issues and Fixes

### Issue 1: Python Path Wrong

The service might not be finding Python. Check:

```bash
which python3
```

Then update the service file to use the correct path.

### Issue 2: Environment File Not Loading

The `.env` file might not be loading correctly. Let's fix the service file.

### Issue 3: User Permissions

The service might need different user permissions.

## Quick Fix - Update Service File

**On your Raspberry Pi:**

```bash
cd ~/smart_plant_pi

# Stop the service first
sudo systemctl stop smart-plant-sensor.service

# Find Python path
PYTHON_PATH=$(which python3)
echo "Python path: $PYTHON_PATH"

# Update service file with correct paths
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$HOME/smart_plant_pi
Environment="DATABASE_URL=$(grep DATABASE_URL $HOME/smart_plant_pi/.env | cut -d'=' -f2-)"
Environment="PLANT_ID=$(grep PLANT_ID $HOME/smart_plant_pi/.env | cut -d'=' -f2 || echo '1')"
ExecStart=$PYTHON_PATH $HOME/smart_plant_pi/send_sensor_data_continuous.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.service
sudo systemctl status smart-plant-sensor.service
```

## Alternative: Test Script Manually First

Before using systemd, test if the script works manually:

```bash
cd ~/smart_plant_pi
python3 send_sensor_data_continuous.py
```

If this works, then the issue is with the systemd service configuration.

## Simpler Alternative: Use nohup Instead

If systemd keeps failing, use nohup to run in background:

```bash
cd ~/smart_plant_pi
nohup python3 send_sensor_data_continuous.py > sensor_output.log 2>&1 &
```

Then check if it's running:
```bash
ps aux | grep send_sensor_data_continuous
tail -f sensor_output.log
```

