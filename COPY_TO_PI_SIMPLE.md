# Quick Setup - Copy Files to Raspberry Pi

## Your Raspberry Pi Info:
- **Username**: s-plant-pi
- **IP Address**: 10.68.200.197

## Step 1: Test SSH Connection

First, make sure you can SSH into your Pi:

```bash
ssh s-plant-pi@10.68.200.197
```

If this works, proceed to Step 2. If not, you may need to:
- Enable password authentication on Raspberry Pi
- Set up SSH keys
- Or use one of the alternative methods below

## Step 2: Copy Files (Choose One Method)

### Method A: SCP (if SSH works)

From your Mac terminal:
```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
scp -r raspberry_pi/ s-plant-pi@10.68.200.197:~/
```

### Method B: Manual Copy via SSH

If SCP doesn't work, SSH in and create files manually:

```bash
# 1. SSH into Raspberry Pi
ssh s-plant-pi@10.68.200.197

# 2. Create directory
mkdir -p ~/raspberry_pi
cd ~/raspberry_pi

# 3. Create files (you can copy-paste from your Mac)
nano send_sensor_data.py
# Paste contents from raspberry_pi/send_sensor_data.py

nano test_connection.py
# Paste contents from raspberry_pi/test_connection.py

nano setup.sh
# Paste contents from raspberry_pi/setup.sh

nano check_setup.py
# Paste contents from raspberry_pi/check_setup.py

# 4. Create .env file
nano .env
# Add:
# DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
# PLANT_ID=1

# 5. Make executable
chmod +x setup.sh send_sensor_data.py test_connection.py check_setup.py
```

### Method C: Use USB Drive

1. Copy `raspberry_pi` folder to USB drive
2. Plug into Raspberry Pi
3. On Pi:
   ```bash
   mkdir -p ~/raspberry_pi
   cp /media/usb/raspberry_pi/* ~/raspberry_pi/
   cd ~/raspberry_pi
   chmod +x setup.sh
   ./setup.sh
   ```

## Step 3: Run Setup

Once files are copied:

```bash
ssh s-plant-pi@10.68.200.197
cd ~/raspberry_pi
chmod +x setup.sh
./setup.sh
```

## Step 4: Verify Setup

```bash
cd ~/smart_plant_pi  # Setup script creates this directory
python3 check_setup.py
python3 test_connection.py
```

## Troubleshooting SSH

If SSH authentication fails:

1. **Enable password authentication** (on Raspberry Pi):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change: PasswordAuthentication yes
   # Then: sudo systemctl restart ssh
   ```

2. **Or set up SSH keys** (on your Mac):
   ```bash
   ssh-copy-id s-plant-pi@10.68.200.197
   ```

3. **Or use a different method** (USB, Git, etc.)

