#!/bin/bash
# Setup Automatic Sensor Readings on Raspberry Pi
# Run this script on your Raspberry Pi to set up automatic readings every 5 minutes

set -e

echo "=========================================="
echo "Setting up Automatic Sensor Readings"
echo "=========================================="
echo ""

WORK_DIR="$HOME/smart_plant_pi"
PLANT_ID="${PLANT_ID:-1}"  # Default to Plant ID 1

# Check if directory exists
if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: $WORK_DIR not found"
    echo "   Make sure you've set up the Raspberry Pi files first"
    exit 1
fi

# Check if script exists
if [ ! -f "$WORK_DIR/send_sensor_data.py" ]; then
    echo "❌ Error: send_sensor_data.py not found in $WORK_DIR"
    exit 1
fi

# Get Plant ID from .env or ask user
if [ -f "$WORK_DIR/.env" ]; then
    ENV_PLANT_ID=$(grep "^PLANT_ID=" "$WORK_DIR/.env" | cut -d'=' -f2)
    if [ ! -z "$ENV_PLANT_ID" ]; then
        PLANT_ID="$ENV_PLANT_ID"
        echo "✅ Found PLANT_ID=$PLANT_ID in .env file"
    fi
fi

echo "Plant ID: $PLANT_ID"
echo ""

# Create log file
LOG_FILE="$HOME/sensor_log.txt"
echo "Log file: $LOG_FILE"
echo ""

# Method 1: Using Cron (Recommended)
echo "[1/2] Setting up cron job..."
CRON_JOB="*/5 * * * * cd $WORK_DIR && /usr/bin/python3 send_sensor_data.py $PLANT_ID >> $LOG_FILE 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "send_sensor_data.py"; then
    echo "⚠️  Cron job already exists. Updating..."
    # Remove old cron job
    crontab -l 2>/dev/null | grep -v "send_sensor_data.py" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added!"
echo ""
echo "Cron job details:"
echo "  Schedule: Every 5 minutes"
echo "  Command: cd $WORK_DIR && python3 send_sensor_data.py $PLANT_ID"
echo "  Log file: $LOG_FILE"
echo ""

# Verify cron job
echo "Current crontab:"
crontab -l | grep "send_sensor_data.py"
echo ""

# Test run
echo "[2/2] Testing sensor data script..."
cd "$WORK_DIR"
if python3 send_sensor_data.py "$PLANT_ID" >> "$LOG_FILE" 2>&1; then
    echo "✅ Test run successful!"
    echo "   Check log: tail -f $LOG_FILE"
else
    echo "⚠️  Test run had issues. Check log: $LOG_FILE"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Automatic readings will run every 5 minutes."
echo ""
echo "Commands:"
echo "  View logs: tail -f $LOG_FILE"
echo "  Check cron: crontab -l"
echo "  Remove cron: crontab -e (then delete the line)"
echo ""
echo "To change the interval, edit crontab:"
echo "  crontab -e"
echo ""
echo "Common intervals:"
echo "  Every 1 minute: */1 * * * *"
echo "  Every 5 minutes: */5 * * * *"
echo "  Every 10 minutes: */10 * * * *"
echo "  Every hour: 0 * * * *"

