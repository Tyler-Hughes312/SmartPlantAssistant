# Fix .env File - DATABASE_URL Error

Your backend is crashing because the DATABASE_URL in your .env file is invalid.

## Fix Your .env File

Edit your `.env` file and make sure DATABASE_URL is set correctly:

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
nano .env
```

Make sure you have this line (replace any placeholder values):

```bash
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

## Quick Fix Command

Run this to fix your .env file:

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant

# Backup current .env
cp .env .env.backup

# Create correct .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-secret-key-change-this
NWS_USER_AGENT=SmartPlantAssistant-tyler.hughes@vanderbilt.edu
EOF
```

## Then Restart Backend

```bash
cd backend
python3 app.py
```

The backend should start successfully now!

