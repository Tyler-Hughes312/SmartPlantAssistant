# Fix for Raspberry Pi Package Installation Error

The error you're seeing is because newer Raspberry Pi OS protects system Python packages.

## Quick Fix: Install with --user flag

Run this on your Raspberry Pi:

```bash
cd ~/smart_plant_pi
pip3 install --user psycopg2-binary python-dotenv
```

If that still doesn't work, use:

```bash
pip3 install --user --break-system-packages psycopg2-binary python-dotenv
```

## Alternative: Use apt (System Packages)

```bash
sudo apt update
sudo apt install -y python3-psycopg2 python3-dotenv
```

## After Installing, Test:

```bash
cd ~/smart_plant_pi
python3 test_connection.py
python3 send_sensor_data.py 1
```

## If Python Can't Find Packages

If you get "ModuleNotFoundError" after installing with --user, you may need to add to PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"
```

Add this to your ~/.bashrc to make it permanent:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
```

