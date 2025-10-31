# Troubleshooting Login/Registration Issues

If login and registration are failing after setting up environment variables, try these steps:

## 1. Restart the Backend Server

The SECRET_KEY fix requires a backend restart:
```bash
# Stop the backend (Ctrl+C or ./stop.sh)
# Then restart:
cd backend
source venv/bin/activate
pip install python-dotenv  # If not already installed
python app.py
```

## 2. Clear Browser Cookies

The old session cookies were signed with a different SECRET_KEY:
1. Open browser developer tools (F12)
2. Go to Application/Storage tab
3. Clear cookies for `localhost:5001` and `localhost:3001`
4. Refresh the page

## 3. Check Backend Logs

Look for error messages in the terminal where the backend is running:
- Check for "Login error:" or "Registration error:" messages
- Look for database connection errors
- Check for CORS errors

## 4. Verify Environment Variables

Make sure `.env` file exists in project root:
```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant
cat .env
```

Should see:
```
NWS_USER_AGENT=SmartPlantAssistant-tyler.i.hughes@vanderbilt.edu
# Optional:
# OPENAI_API_KEY=your_key_here
# SECRET_KEY=your_secret_here
```

## 5. Test Endpoints Directly

Test login endpoint:
```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  -c cookies.txt -v
```

## 6. Check Frontend Console

Open browser console (F12) and look for:
- Network errors (401, 500, CORS errors)
- JavaScript errors
- Failed API calls

## 7. Common Issues

### Issue: "Invalid username or password"
- User might not exist - try registering first
- Password might be incorrect
- Database might not be initialized

### Issue: CORS errors
- Backend must be running on port 5001
- Frontend must be on port 3001
- Check CORS origins in backend/app.py

### Issue: Session cookies not working
- SECRET_KEY must be consistent (already fixed)
- Browser must allow cookies
- Make sure `withCredentials: true` in frontend API calls

