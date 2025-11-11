# Copy Setup Files to Raspberry Pi

## Step 1: Copy Files from Mac to Raspberry Pi

**On your Mac, run these commands:**

```bash
# Copy the setup script
scp /Users/tylerhughes/Projects/SmartPlantAssistant/raspberry_pi/setup_10_second_readings.sh s-plant-pi@10.68.200.197:~/smart_plant_pi/

# Copy the continuous sensor script
scp /Users/tylerhughes/Projects/SmartPlantAssistant/raspberry_pi/send_sensor_data_continuous.py s-plant-pi@10.68.200.197:~/smart_plant_pi/
```

## Step 2: SSH into Raspberry Pi

```bash
ssh s-plant-pi@10.68.200.197
```

## Step 3: Verify Files Are There

```bash
cd ~/smart_plant_pi
ls -la
```

You should see:
- `setup_10_second_readings.sh`
- `send_sensor_data_continuous.py`
- `.env`
- `test_connection.py`

## Step 4: Run Setup

```bash
chmod +x setup_10_second_readings.sh
sudo ./setup_10_second_readings.sh
```

## Alternative: Create Files Directly on Raspberry Pi

If SCP doesn't work, you can create the files directly on the Pi:

**On Raspberry Pi:**

```bash
cd ~/smart_plant_pi
nano setup_10_second_readings.sh
```

Then paste the contents (I'll provide a simpler version below).

