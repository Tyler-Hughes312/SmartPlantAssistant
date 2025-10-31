#!/bin/bash

# Start Smart Plant Assistant - Both Backend and Frontend

echo "🚀 Starting Smart Plant Assistant..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start Backend (Flask)
echo "📡 Starting Flask backend on port 5001..."
cd backend
source venv/bin/activate
python app.py > /tmp/flask.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check /tmp/flask.log for errors."
    exit 1
fi

echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Start Frontend (React)
echo "🌐 Starting React frontend on port 3001..."
cd frontend
npm start > /tmp/react.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start. Check /tmp/react.log for errors."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Smart Plant Assistant is running!"
echo ""
echo "📡 Backend API:  http://localhost:5001"
echo "🌐 Frontend UI:  http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop both services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for user interrupt
wait

