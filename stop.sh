#!/bin/bash

# Stop Smart Plant Assistant services

echo "🛑 Stopping Smart Plant Assistant..."

# Kill Flask backend
pkill -f "python.*app.py" && echo "✅ Stopped Flask backend" || echo "⚠️  Flask backend not running"

# Kill React frontend
pkill -f "react-scripts" && echo "✅ Stopped React frontend" || echo "⚠️  React frontend not running"

echo ""
echo "✅ All services stopped"

