# Test User Created in Neon Database ✅

## Test User Credentials

**Username**: `testuser`  
**Password**: `testpass123`  
**Email**: `test@example.com`  
**Location**: Nashville, TN  
**User ID**: 1

## Test Plant Created

**Plant Name**: Test Plant  
**Plant ID**: 1  
**Sensor ID**: sensor-001  
**User ID**: 1

## Login to Your Flask App

1. Start your Flask backend:
   ```bash
   cd backend
   python3 app.py
   ```

2. Open your browser: `http://localhost:3000`

3. Login with:
   - Username: `testuser`
   - Password: `testpass123`

## For Raspberry Pi

Update your `.env` file on Raspberry Pi:
```bash
PLANT_ID=1
```

This matches the test plant we just created!

## Verify in Database

You can check users and plants:
```bash
cd backend
python3 -c "from app import app, db, User, Plant; app.app_context().push(); print('Users:', [(u.id, u.username) for u in User.query.all()]); print('Plants:', [(p.id, p.name, p.user_id) for p in Plant.query.all()])"
```

