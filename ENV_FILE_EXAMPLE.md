# .env File Example

This document shows exactly what your `.env` file should look like. Copy this template and fill in your actual values.

## Location

Place the `.env` file in the **project root** directory (same level as `backend/` and `frontend/` folders):

```
SmartPlantAssistant/
├── .env              ← Put it here
├── backend/
├── frontend/
└── ...
```

## Complete .env Template

```bash
# ============================================
# Smart Plant Assistant - Environment Variables
# ============================================

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Option 1: Neon Postgres (Production/Cloud)
# Get this from your Neon dashboard: https://console.neon.tech
# Format: postgresql://username:password@host:port/dbname?sslmode=require
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Option 2: SQLite (Local Development)
# Uncomment this line and comment out DATABASE_URL above to use SQLite locally
# DATABASE_URL=sqlite:///smart_plant.db

# ============================================
# FLASK SECURITY
# ============================================

# Secret key for Flask sessions (REQUIRED)
# Generate a secure key: python3 -c "import secrets; print(secrets.token_hex(32))"
# Or use: openssl rand -hex 32
SECRET_KEY=your-secret-key-change-this-to-a-random-64-character-hex-string

# ============================================
# WEATHER API
# ============================================

# NWS (National Weather Service) User-Agent (REQUIRED for weather data)
# Use your email address - this is required by NWS API terms of service
NWS_USER_AGENT=SmartPlantAssistant-your-email@example.com

# ============================================
# OPENAI API (Optional - for chatbot)
# ============================================

# Only needed if you want to use the chatbot feature
# Get your API key from: https://platform.openai.com/api-keys
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# RASPBERRY PI CONFIGURATION (Optional)
# ============================================

# Plant ID for your Raspberry Pi sensor (if using)
# PLANT_ID=1

# ============================================
# FLASK SERVER CONFIGURATION (Optional)
# ============================================

# Port for Flask backend (default: 5001)
# PORT=5001
```

## Example with Real Values

Here's what it might look like with actual values filled in:

```bash
# Database - Neon Postgres
DATABASE_URL=postgresql://myuser:mypassword123@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Flask Secret Key (64 character hex string)
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# Weather API
NWS_USER_AGENT=SmartPlantAssistant-tyler.hughes@vanderbilt.edu

# OpenAI (optional)
OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

# Raspberry Pi
PLANT_ID=1
```

## How to Create Your .env File

### Method 1: Copy Template

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
cp ENV_FILE_EXAMPLE.md .env
# Then edit .env with your actual values
nano .env
```

### Method 2: Create from Scratch

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
nano .env
# Paste the template above and fill in your values
```

### Method 3: Generate Secret Key

```bash
# Generate a secure SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
# Copy the output and add it to your .env file
```

## Required vs Optional Variables

### ✅ Required Variables

1. **SECRET_KEY** - Always required for Flask sessions
2. **NWS_USER_AGENT** - Required if using weather features
3. **DATABASE_URL** - Required if using Neon Postgres (or leave unset for SQLite)

### ⚪ Optional Variables

1. **OPENAI_API_KEY** - Only needed for chatbot feature
2. **PLANT_ID** - Only needed for Raspberry Pi scripts
3. **PORT** - Only needed if you want a different port than 5001

## Neon Database URL Format

Your Neon connection string should look like this:

```
postgresql://[username]:[password]@[host]/[database]?sslmode=require
```

Example:
```
postgresql://neondb_owner:AbC123XyZ@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important**: 
- Make sure `sslmode=require` is included (the code will add it automatically if missing)
- Never commit your `.env` file to git (it's already in `.gitignore`)

## Testing Your .env File

After creating your `.env` file, test it:

```bash
# Test database connection
python3 backend/test_neon_connection.py

# Or test Flask app loads correctly
cd backend
python3 -c "from app import app; print('✅ App loaded successfully')"
```

## Troubleshooting

### "DATABASE_URL not found"
- Make sure `.env` is in the project root (not in `backend/` folder)
- Check the file is named exactly `.env` (not `.env.txt`)

### "Invalid connection string"
- Make sure your Neon URL includes `?sslmode=require`
- Check username, password, host, and database name are correct

### "SECRET_KEY not set"
- Generate a new key: `python3 -c "import secrets; print(secrets.token_hex(32))"`
- Add it to your `.env` file


