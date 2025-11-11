# Debugging 500 Error on Login

## What to Check

### 1. Check Backend Terminal Logs
The backend should print detailed error information. Look for:
- `Login error [ErrorType]: error message`
- `FULL TRACEBACK:` section

**This will tell us exactly what's failing.**

### 2. Check Browser Console
In browser console (F12), look for the full error response:
```javascript
// The response should now include:
{
  "error": "Login failed",
  "error_type": "SomeErrorType",
  "details": "Specific error message"
}
```

### 3. Common Causes

#### Issue: AttributeError - 'NoneType' object has no attribute...
**Cause**: User object missing an attribute (location, latitude, longitude)
**Fix**: Already added safe handling with `getattr()`

#### Issue: RuntimeError - Working outside of request context
**Cause**: Session/session access outside request
**Fix**: Shouldn't happen in endpoint, but might if database connection issues

#### Issue: SQLAlchemy errors
**Cause**: Database connection or query issues
**Fix**: Check database file exists and is accessible

#### Issue: JSON serialization errors
**Cause**: Can't serialize user data (e.g., datetime objects)
**Fix**: Already handling None values, but might be datetime issues

### 4. Quick Test

Run this to see the exact error:
```bash
cd backend
python test_login_simple.py
```

### 5. Check What Backend Logs Show

When you try to login, the backend terminal should show:
1. `DEBUG login: Logged in user X` (if it gets that far)
2. `Login error [ErrorType]: ...` (if error occurs)
3. Full traceback

**Copy the error from backend terminal and share it.**

## Next Steps

1. **Check backend terminal** - Look for the error message and traceback
2. **Share the error** - Copy the error from backend logs
3. **Check database** - Make sure `smart_plant.db` file exists and is readable

The improved error handling should now show exactly what's failing!



