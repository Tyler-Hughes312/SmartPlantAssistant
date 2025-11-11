#!/bin/bash
# Setup Automatic Sensor Readings - Every 10 Seconds
# This creates a systemd service that runs continuously

set -e

echo "=========================================="
echo "Setting up Automatic Sensor Readings (10 seconds)"
echo "=========================================="
echo ""

WORK_DIR="$HOME/smart_plant_pi"
PLANT_ID="${PLANT_ID:-1}"

# Check if directory exists
if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: $WORK_DIR not found"
    exit 1
fi

# Get Plant ID from .env
if [ -f "$WORK_DIR/.env" ]; then
    ENV_PLANT_ID=$(grep "^PLANT_ID=" "$WORK_DIR/.env" | cut -d'=' -f2)
    if [ ! -z "$ENV_PLANT_ID" ]; then
        PLANT_ID="$ENV_PLANT_ID"
    fi
fi

echo "Plant ID: $PLANT_ID"
echo "Interval: 10 seconds"
echo ""

# Create the continuous script if it doesn't exist
if [ ! -f "$WORK_DIR/send_sensor_data_continuous.py" ]; then
    echo "❌ Error: send_sensor_data_continuous.py not found"
    echo "   Make sure you've copied all files to Raspberry Pi"
    exit 1
fi

chmod +x "$WORK_DIR/send_sensor_data_continuous.py"

# Create systemd service
echo "[1/2] Creating systemd service..."
sudo tee /etc/systemd/system/smart-plant-sensor.service > /dev/null << EOF
[Unit]
Description=Smart Plant Sensor Data Collector (10 seconds)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$WORK_DIR
EnvironmentFile=$WORK_DIR/.env
ExecStart=/usr/bin/python3 $WORK_DIR/send_sensor_data_continuous.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"
echo ""

# Reload systemd
echo "[2/2] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable smart-plant-sensor.service
sudo systemctl start smart-plant-sensor.service

echo "✅ Service enabled and started!"
echo ""

# Check status
echo "Service status:"
sudo systemctl status smart-plant-sensor.service --no-pager -l | head -15
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Sensor readings will be sent every 10 seconds."
echo ""
echo "Commands:"
echo "  View logs: sudo journalctl -u smart-plant-sensor.service -f"
echo "  Check status: sudo systemctl status smart-plant-sensor.service"
echo "  Stop: sudo systemctl stop smart-plant-sensor.service"
echo "  Start: sudo systemctl start smart-plant-sensor.service"
echo "  Restart: sudo systemctl restart smart-plant-sensor.service"
echo "  Disable: sudo systemctl disable smart-plant-sensor.service"
echo ""

