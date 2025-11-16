#!/bin/bash

# Start Smart Plant Assistant - Both Backend and Frontend

echo "🚀 Starting Smart Plant Assistant..."
echo ""

# Check if services are already running
if lsof -i :5001 -i :5000 | grep -q LISTEN; then
    echo "⚠️  Backend may already be running on port 5000/5001"
    echo "   Run './stop.sh' first if you want to restart"
    echo ""
fi

if lsof -i :3001 | grep -q LISTEN; then
    echo "⚠️  Frontend may already be running on port 3001"
    echo "   Run './stop.sh' first if you want to restart"
    echo ""
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start Backend (Flask)
echo "📡 Starting Flask backend..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
    # Ensure all dependencies are installed
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt
fi

# Get port from environment or use default
PORT=${PORT:-5001}
echo "   Port: $PORT"

python app.py > /tmp/flask.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check /tmp/flask.log for errors."
    tail -20 /tmp/flask.log
    exit 1
fi

echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Start Frontend (React)
echo "🌐 Starting React frontend..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

PORT=3001 npm start > /tmp/react.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start. Check /tmp/react.log for errors."
    tail -20 /tmp/react.log
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Smart Plant Assistant is running!"
echo ""
echo "📡 Backend API:  http://localhost:$PORT"
echo "🌐 Frontend UI:  http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/flask.log"
echo "   Frontend: tail -f /tmp/react.log"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for user interrupt
wait

