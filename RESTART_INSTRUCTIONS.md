# Quick Fix: Restart Everything

## Step 1: Start Backend (Terminal 1)

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant/backend
python3 app.py
```

Wait until you see:
```
 * Running on http://127.0.0.1:5001
```

## Step 2: Start Frontend (Terminal 2)

```bash
cd /Users/tylerhughes/Projects/SmartPlantAssistant/frontend
npm start
```

## Step 3: Test Login

1. Open browser: `http://localhost:3000`
2. Open DevTools (F12) → Console tab
3. Try to login with:
   - Username: `testuser`
   - Password: `testpass123`
4. Check Console for any errors

## Step 4: If Still Getting 500 Error

Check the backend terminal for error messages. The error will show there.

Common fixes:
- Clear browser cookies (DevTools → Application → Cookies → Clear)
- Make sure backend is running on port 5001
- Check browser console for CORS errors

