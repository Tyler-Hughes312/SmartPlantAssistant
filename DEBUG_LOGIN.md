# Debug Login Issues

## Quick Fix Steps

### 1. Reset Test User Password
```bash
cd backend
python reset_test_user.py
```

This ensures the password is definitely `testpass123`.

### 2. Check Backend is Running
Make sure backend is running on port 5001:
```bash
cd backend
source venv/bin/activate
python app.py
```

Look for: `Running on http://127.0.0.1:5001`

### 3. Clear Browser Cookies
**CRITICAL**: Clear ALL cookies for localhost:
- Open Developer Tools (F12)
- Application → Cookies
- Delete cookies for:
  - `localhost:3001`
  - `localhost:5001`
  - `127.0.0.1:5001`
- Or use Incognito/Private window

### 4. Test Login
1. Open http://localhost:3001
2. Try login: `testuser` / `testpass123`
3. Check browser console (F12) for errors
4. Check Network tab:
   - Login request should return 200
   - Should see `Set-Cookie` in response headers
   - Next request to `/api/user` should include `Cookie` header

## Debugging

### Check Backend Logs
When you try to login, you should see:
```
DEBUG login: Logged in user 2, session keys=[...]
DEBUG login: _user_id in session=2
```

### Check Browser Console
Open console (F12) and look for:
- Network errors
- CORS errors
- JavaScript errors

### Test Login Directly
```bash
cd backend
python test_login_direct.py
```

### Check Session Status
After logging in, in browser console:
```javascript
fetch('/api/debug/session', { credentials: 'include' })
  .then(r => r.json())
  .then(console.log)
```

Should show:
```json
{
  "session_keys": ["_user_id", "_fresh", ...],
  "user_id": 2,
  "is_authenticated": true,
  "user": { "id": 2, "username": "testuser" }
}
```

## Common Issues

### Issue: "Login failed" but backend shows success
**Cause**: Cookie not being sent to `/api/user` endpoint
**Fix**: Clear cookies and restart both servers

### Issue: CORS errors in console
**Cause**: Frontend not sending credentials or CORS misconfigured
**Fix**: 
- Verify `withCredentials: true` in `api.js`
- Check CORS origins include `http://localhost:3001`

### Issue: Session cookie not in response headers
**Cause**: Flask session not being set
**Fix**: 
- Check backend logs for `DEBUG login:` messages
- Verify `session.permanent = True` is being set

### Issue: Cookie set but not sent on next request
**Cause**: SameSite policy or domain mismatch
**Fix**:
- Check cookie domain is `None` or `localhost`
- Verify SameSite is `Lax` (not `Strict` or `None`)

## Still Not Working?

1. Check all debug logs
2. Test with `test_login_direct.py`
3. Check browser Network tab carefully
4. Try in Incognito window
5. Restart both servers



