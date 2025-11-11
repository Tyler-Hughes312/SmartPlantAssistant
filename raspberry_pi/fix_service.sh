#!/bin/bash
# Fixed Setup Script - Handles common issues

WORK_DIR="$HOME/smart_plant_pi"

echo "Fixing service configuration..."

# Stop service if running
sudo systemctl stop smart-plant-sensor.service 2>/dev/null || true

# Get Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH="/usr/bin/python3"
fi

# Get environment variables
if [ -f "$WORK_DIR/.env" ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" "$WORK_DIR/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    PLANT_ID=$(grep "^PLANT_ID=" "$WORK_DIR/.env" | cut -d'=' -f2 || echo "1")
else
    echo "❌ .env file not found!"
    exit 1
fi

echo "Python: $PYTHON_PATH"
echo "Plant ID: $PLANT_ID"
echo "Working Dir: $WORK_DIR"

# Create service file
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORK_DIR
Environment="DATABASE_URL=$DATABASE_URL"
Environment="PLANT_ID=$PLANT_ID"
ExecStart=$PYTHON_PATH $WORK_DIR/send_sensor_data_continuous.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service

sleep 2

# Check status
echo ""
echo "Service status:"
sudo systemctl status smart-plant-sensor.service --no-pager -l | head -20

echo ""
echo "Recent logs:"
sudo journalctl -u smart-plant-sensor.service -n 10 --no-pager

