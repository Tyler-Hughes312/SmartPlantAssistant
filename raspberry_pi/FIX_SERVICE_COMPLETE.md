# Fix Service - Use Direct Environment Variables

The service can't find the .env file. Let's fix it by reading the .env file and setting Environment variables directly.

## On Your Raspberry Pi - Run This:

```bash
cd ~/smart_plant_pi

# Stop the service
sudo systemctl stop smart-plant-sensor.service

# Read .env file and get variables
export $(grep -v '^#' .env | xargs)
PYTHON_PATH=$(which python3)
SCRIPT_PATH="$HOME/smart_plant_pi/send_sensor_data_continuous.py"

echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "PLANT_ID: $PLANT_ID"
echo "Python: $PYTHON_PATH"
echo "Script: $SCRIPT_PATH"

# Verify script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found at $SCRIPT_PATH"
    exit 1
fi

# Create service file with direct Environment variables
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$HOME/smart_plant_pi
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

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service

# Wait and check status
sleep 3
sudo systemctl status smart-plant-sensor.service --no-pager -l
```

## If That Doesn't Work - Use Absolute Paths:

```bash
cd ~/smart_plant_pi

# Get absolute paths
ABS_HOME=$(echo $HOME)
ABS_SCRIPT="$ABS_HOME/smart_plant_pi/send_sensor_data_continuous.py"
PYTHON_PATH=$(which python3)

# Read .env
export $(grep -v '^#' .env | xargs)

# Create service with absolute paths
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$ABS_HOME/smart_plant_pi
Environment="DATABASE_URL=$DATABASE_URL"
Environment="PLANT_ID=$PLANT_ID"
ExecStart=$PYTHON_PATH $ABS_SCRIPT
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart smart-plant-sensor.service
sudo systemctl status smart-plant-sensor.service
```

## Verify Script Works Manually First:

Before fixing the service, test the script works:

```bash
cd ~/smart_plant_pi
source .env
python3 send_sensor_data_continuous.py
```

Press Ctrl+C after a few readings to stop it. If this works, then the service should work too.

