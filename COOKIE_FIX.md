# Cookie/Session Fix Instructions

## Problem
Login and registration failing due to cookie/session issues between frontend (port 3001) and backend (port 5001).

## Changes Made

### Backend (`app.py`)
1. **Fixed registration endpoint** - Now sets `session.permanent = True` like login does
2. **Enhanced session configuration** - Added explicit cookie settings
3. **Added debug endpoints** - `/api/debug/session` to check session status
4. **Added debug logging** - More verbose session debugging

### Frontend (`AuthContext.js`)
1. **Fixed register flow** - Now calls `checkAuth()` after registration (like login does)

## Testing

### Step 1: Test Cookie Handling
```bash
cd backend
python test_cookies.py
```

This will:
- Register a new user
- Test login
- Verify cookies are set and persist
- Test protected endpoint access

### Step 2: Clear Browser State
**IMPORTANT**: You MUST clear cookies and restart both servers:

1. **Clear Browser Cookies**:
   - Open Developer Tools (F12)
   - Go to Application → Cookies
   - Delete ALL cookies for `localhost:3001` and `localhost:5001`
   - Or use Incognito/Private window

2. **Restart Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```
   
3. **Restart Frontend**:
   ```bash
   cd frontend
   npm start
   ```

### Step 3: Test Login
1. Open browser: http://localhost:3001
2. Try logging in with: `testuser` / `testpass123`
3. Check browser console (F12) for any errors
4. Check Network tab to see if cookies are being sent/received

### Step 4: Debug Session (if still failing)
```bash
# After logging in, check session status:
curl http://localhost:5001/api/debug/session \
  -H "Cookie: session=<your-session-cookie>" \
  --cookie-jar cookies.txt \
  --cookie cookies.txt
```

Or in browser console:
```javascript
fetch('/api/debug/session', { credentials: 'include' })
  .then(r => r.json())
  .then(console.log)
```

## Common Issues

### Issue 1: Cookies Not Being Sent
**Symptom**: Network tab shows no cookies in request headers

**Fix**:
- Verify `withCredentials: true` in `api.js`
- Check that proxy in `package.json` is correct
- Clear cookies and try again

### Issue 2: Cookies Set But Session Invalid
**Symptom**: `/api/user` returns 401 even after login

**Fix**:
- Check backend logs for session debug info
- Verify SECRET_KEY is consistent (check `.env` file)
- Restart backend to ensure new SECRET_KEY is loaded

### Issue 3: CORS Errors
**Symptom**: Browser console shows CORS errors

**Fix**:
- Verify CORS origins include `http://localhost:3001`
- Check that `supports_credentials=True` in CORS config
- Ensure frontend proxy is working

## Verification

After fixing, you should see:
1. ✅ Login sets a cookie (check Network tab → Response Headers → `Set-Cookie`)
2. ✅ Subsequent requests include cookie (check Network tab → Request Headers → `Cookie`)
3. ✅ `/api/user` returns 200 after login
4. ✅ Backend logs show: `DEBUG login: Logged in user X`

## Still Failing?

Run diagnostic:
```bash
cd backend
python test_diagnostic.py
python test_auth.py
python test_cookies.py
```

Check:
- Backend terminal logs
- Browser console (F12)
- Network tab in browser (check request/response headers)
- Cookies in Application tab

