# Port 3000 is Used by Grafana

## Issue Found

Port 3000 is currently being used by **Grafana** (a monitoring tool), not your React app.

## Solutions

### Option 1: Use Port 3001 (Easiest)

Your React app was originally configured for port 3001. Let's use that:

```bash
cd frontend
# Change back to port 3001
sed -i '' 's/PORT=3000/PORT=3001/' package.json
npm start
```

Then access your app at: **http://localhost:3001**

### Option 2: Stop Grafana and Use Port 3000

If you want to use port 3000, stop Grafana first:

```bash
# Find Grafana process
ps aux | grep grafana

# Stop it (replace PID with actual process ID)
kill <PID>

# Or if running in Docker
docker ps | grep grafana
docker stop <container_id>
```

### Option 3: Keep Both Running

- Grafana: http://localhost:3000
- Your React App: http://localhost:3001

## Quick Fix - Use Port 3001

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant/frontend
# Revert to port 3001
sed -i '' 's/PORT=3000/PORT=3001/' package.json
npm start
```

Then open: **http://localhost:3001**

