# Fix: No such file or directory error

The service can't find the Python executable or script. Let's check and fix with absolute paths.

## On Your Raspberry Pi - Run This Complete Fix:

```bash
cd ~/smart_plant_pi

# Stop the service
sudo systemctl stop smart-plant-sensor.service
sudo systemctl disable smart-plant-sensor.service

# Find actual paths
PYTHON_PATH=$(which python3)
SCRIPT_PATH=$(realpath send_sensor_data_continuous.py)
WORK_DIR=$(pwd)
USER_NAME=$(whoami)

echo "=== Checking Paths ==="
echo "Python: $PYTHON_PATH"
echo "Script: $SCRIPT_PATH"
echo "Work Dir: $WORK_DIR"
echo "User: $USER_NAME"

# Verify files exist
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found!"
    exit 1
fi

if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python not found!"
    exit 1
fi

# Read .env variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "PLANT_ID: $PLANT_ID"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Create service file - NO EnvironmentFile, use Environment directly
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$WORK_DIR
Environment="DATABASE_URL=$DATABASE_URL"
Environment="PLANT_ID=$PLANT_ID"
ExecStart=$PYTHON_PATH $SCRIPT_PATH
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service

# Wait and check
sleep 3
echo ""
echo "=== Service Status ==="
sudo systemctl status smart-plant-sensor.service --no-pager -l | head -20

echo ""
echo "=== Recent Logs ==="
sudo journalctl -u smart-plant-sensor.service -n 10 --no-pager
```

## If Still Failing - Check What's Actually Wrong:

```bash
# Check if Python works
which python3
python3 --version

# Check if script exists and is executable
ls -la ~/smart_plant_pi/send_sensor_data_continuous.py
file ~/smart_plant_pi/send_sensor_data_continuous.py

# Test running it manually
cd ~/smart_plant_pi
source .env
python3 send_sensor_data_continuous.py
```

## Alternative: Use nohup (Simpler, No systemd)

If systemd keeps failing, just run it in background:

```bash
cd ~/smart_plant_pi
source .env
nohup python3 send_sensor_data_continuous.py > sensor_output.log 2>&1 &

# Check if running
ps aux | grep send_sensor_data_continuous

# View output
tail -f sensor_output.log
```

This will run continuously and send data every 10 seconds without systemd.

