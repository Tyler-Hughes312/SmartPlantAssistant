# Raspberry Pi Sensor ID Guide

## What is Sensor ID?

The `sensor_id` is a **unique identifier** for each plant/sensor setup. It's stored in the `plants` table and must be unique across all plants.

## Current Setup

You already have a test plant with:
- **Plant ID**: 1
- **Sensor ID**: `sensor-001`
- **Plant Name**: Test Plant

## For Your Raspberry Pi

You have **two options**:

### Option 1: Use Plant ID (Easiest - Recommended)

Your Raspberry Pi script uses `plant_id` by default. Just use:

```bash
python3 send_sensor_data.py 1
```

The `.env` file should have:
```bash
PLANT_ID=1
```

### Option 2: Use Sensor ID

If you want to use `sensor_id` instead, you would need to modify the script to look up the plant by `sensor_id`. But **you don't need to do this** - using `plant_id` is simpler.

## What Sensor ID Should You Use?

When creating a **new plant** in your Flask app, you'll need to provide a unique `sensor_id`. Examples:

- `raspberry-pi-001`
- `sensor-001` (already used by test plant)
- `pi-sensor-1`
- `my-plant-sensor`
- `living-room-plant`

**Important**: Each `sensor_id` must be unique. If you try to create a plant with `sensor-001`, it will fail because it's already taken.

## For Your Current Setup

Since you're using the test plant (Plant ID: 1), you don't need to worry about `sensor_id` on the Raspberry Pi. Just use:

```bash
# On Raspberry Pi
python3 send_sensor_data.py 1
```

Or set in `.env`:
```bash
PLANT_ID=1
```

## Summary

- **For Raspberry Pi**: Use `PLANT_ID=1` (you don't need to set sensor_id)
- **When creating new plants**: Choose a unique `sensor_id` like `raspberry-pi-001`
- **Current test plant**: Already has `sensor_id: sensor-001`

The Raspberry Pi script uses `plant_id` to send data, so you're all set!

