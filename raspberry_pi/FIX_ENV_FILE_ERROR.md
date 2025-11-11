# Fix: Failed to load environment files

The error is because systemd can't find the .env file. Let's fix it by using Environment variables directly.

## On Your Raspberry Pi:

```bash
cd ~/smart_plant_pi

# Stop the service
sudo systemctl stop smart-plant-sensor.service

# Read environment variables from .env file
source .env
PYTHON_PATH=$(which python3)

# Create service file with Environment variables (not EnvironmentFile)
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

# Check status
sleep 2
sudo systemctl status smart-plant-sensor.service
```

## Or Use This One-Liner:

```bash
cd ~/smart_plant_pi && \
sudo systemctl stop smart-plant-sensor.service && \
source .env && \
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
ExecStart=$(which python3) $HOME/smart_plant_pi/send_sensor_data_continuous.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && \
sudo systemctl restart smart-plant-sensor.service && \
sleep 2 && \
sudo systemctl status smart-plant-sensor.service
```

## Verify It's Working:

```bash
# Check status
sudo systemctl status smart-plant-sensor.service

# View logs
sudo journalctl -u smart-plant-sensor.service -f
```

You should see readings being sent every 10 seconds!

