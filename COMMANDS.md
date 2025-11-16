# Quick Start Commands

## Start Everything (Recommended)

```bash
./start.sh
```

This will start both backend and frontend automatically.

## Start Services Separately

### Backend (Flask)
```bash
cd backend
source venv/bin/activate
python app.py
```

Backend runs on: `http://localhost:5001` (or port set in `PORT` env variable)

### Frontend (React)
```bash
cd frontend
npm start
```

Frontend runs on: `http://localhost:3001`

## Stop Everything

```bash
./stop.sh
```

Or manually:
```bash
# Stop backend
pkill -f "python.*app.py"

# Stop frontend
pkill -f "react-scripts"
```

## Check What's Running

```bash
# Check ports
lsof -i :5001 -i :3001 | grep LISTEN

# Or check processes
ps aux | grep -E "app.py|react-scripts"
```

## View Logs

```bash
# Backend logs
tail -f /tmp/flask.log

# Frontend logs
tail -f /tmp/react.log
```

## Environment Variables

Make sure you have a `.env` file in the project root with:
- `DATABASE_URL` - Neon Postgres connection string
- `SECRET_KEY` - Flask secret key
- `NWS_USER_AGENT` - National Weather Service user agent
- `OPENAI_API_KEY` - OpenAI API key (optional, for chatbot)

## First Time Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Frontend
```bash
cd frontend
npm install
```

