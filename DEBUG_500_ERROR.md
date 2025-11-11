# Debugging 500 Error on Login

## Current Status
- ✅ Backend login endpoint works (tested with curl)
- ✅ Model loads successfully
- ✅ User exists in database
- ❌ Browser gets 500 error

## Possible Causes

1. **Model Loading Error** - Fixed by adding try/catch around model import
2. **CORS Issue** - Backend allows both ports 3000 and 3001
3. **Session Cookie Issue** - Cookies are being set correctly
4. **Frontend Request Format** - Check Network tab for exact request

## Debugging Steps

1. **Check Browser Console (F12)**
   - Look for the exact error message
   - Check if it's a CORS error or 500 error

2. **Check Network Tab (F12 → Network)**
   - Click on the `/api/login` request
   - Check:
     - Request URL
     - Request Headers
     - Response Status
     - Response Body (the error details)

3. **Check Backend Logs**
   ```bash
   tail -f backend/backend.log
   ```
   Then try logging in - you should see the error

4. **Test Direct API Call**
   ```bash
   curl -X POST http://localhost:5001/api/login \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass123"}'
   ```

## Quick Fixes Applied

- ✅ Added error handling around model import
- ✅ Backend restarted with better error logging
- ✅ Model loading wrapped in try/catch

## Next Steps

1. Try logging in again
2. Check browser console for exact error
3. Share the error message from Network tab response body

