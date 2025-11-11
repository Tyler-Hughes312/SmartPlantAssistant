# Fix 500 Error on Login

## Step 1: Make sure backend is running

**Stop any existing backend processes:**
```bash
pkill -f "python.*app.py"
```

**Start the backend:**
```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant/backend
python3 app.py
```

You should see:
```
✅ Using Postgres database (Neon)
✅ ML watering model loaded successfully
✅ ML health classifier loaded successfully
 * Running on http://127.0.0.1:5001
```

## Step 2: Test login directly

In a new terminal, test the login endpoint:
```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  -c cookies.txt -v
```

If this works, the issue is with the frontend connection.

## Step 3: Check frontend is using correct URL

Make sure your frontend is configured to use:
- Development: `http://localhost:5001/api` (or `/api` with proxy)
- The React proxy should be set to `http://localhost:5001` in `package.json`

## Step 4: Clear browser cookies

The 500 error might be from a bad session cookie. Clear cookies:
1. Open browser DevTools (F12)
2. Application tab → Cookies → Clear all
3. Try login again

## Step 5: Check browser console

Open browser DevTools → Console tab and look for:
- CORS errors
- Network errors
- Any error messages

## Quick Test Script

Run this to test everything:
```bash
# Test 1: Backend health
curl http://localhost:5001/api/health

# Test 2: Login endpoint
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Test 3: Check if user exists in database
cd backend
python3 -c "from app import app, db, User; app.app_context().push(); u = User.query.filter_by(username='testuser').first(); print(f'User found: {u.username if u else \"NOT FOUND\"}')"
```

## Most Common Issues

1. **Backend not running** - Start it with `python3 app.py`
2. **Wrong port** - Backend should be on port 5001
3. **CORS issue** - Check browser console for CORS errors
4. **Bad session cookie** - Clear browser cookies
5. **Frontend proxy misconfigured** - Check `frontend/package.json` proxy setting

