# Copy Files to Raspberry Pi - Manual Instructions

Your Raspberry Pi details:
- Username: s-plant-pi
- IP: 10.68.200.197

## Method 1: Using SCP with Password (from your Mac)

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
scp -r raspberry_pi/ s-plant-pi@10.68.200.197:~/
```

You'll be prompted for the password. Enter your Raspberry Pi password.

## Method 2: Using SFTP (Interactive)

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
sftp s-plant-pi@10.68.200.197
# Enter password when prompted
put -r raspberry_pi/
exit
```

## Method 3: Using USB Drive (Easiest if network issues)

1. Copy the `raspberry_pi` folder to a USB drive
2. Plug USB into Raspberry Pi
3. On Raspberry Pi:
   ```bash
   mkdir -p ~/raspberry_pi
   cp /media/usb/raspberry_pi/* ~/raspberry_pi/
   cd ~/raspberry_pi
   chmod +x setup.sh
   ./setup.sh
   ```

## Method 4: Clone from Git (if you have a repo)

On Raspberry Pi:
```bash
git clone <your-repo-url> SmartPlantAssistant
cd SmartPlantAssistant/raspberry_pi
chmod +x setup.sh
./setup.sh
```

## Method 5: Manual File Creation (if all else fails)

SSH into Raspberry Pi:
```bash
ssh s-plant-pi@10.68.200.197
```

Then create files manually or use wget/curl to download from a shared location.

## After Files Are Copied

Once files are on Raspberry Pi, SSH in and run:

```bash
ssh s-plant-pi@10.68.200.197
cd ~/raspberry_pi
chmod +x setup.sh
./setup.sh
```

## Quick Test Connection

First, test if you can SSH in:
```bash
ssh s-plant-pi@10.68.200.197
```

If that works, then scp should work too (with password).

