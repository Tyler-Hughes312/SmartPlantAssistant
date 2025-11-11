#!/bin/bash
# Install Sensor Packages - Multiple Methods

echo "Checking Python version..."
python3 --version

echo ""
echo "Method 1: Try system-wide install with sudo..."
sudo pip3 install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    python3 -c "import board; import adafruit_ahtx0; import adafruit_bh1750; print('✅ All packages work!')"
else
    echo ""
    echo "Method 2: Try with --break-system-packages..."
    pip3 install --user --break-system-packages adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750
    
    if [ $? -eq 0 ]; then
        echo "✅ Installation successful!"
        python3 -c "import board; import adafruit_ahtx0; import adafruit_bh1750; print('✅ All packages work!')"
    else
        echo ""
        echo "Method 3: Create virtual environment..."
        cd ~/smart_plant_pi
        python3 -m venv venv
        source venv/bin/activate
        pip install adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 psycopg2-binary python-dotenv
        echo "✅ Virtual environment created!"
        echo "To use: source venv/bin/activate"
    fi
fi

