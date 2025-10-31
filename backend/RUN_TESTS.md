# How to Run Tests

## Quick Test (Recommended)

```bash
cd backend
python test_diagnostic.py
```

This will check:
- App initialization
- Database connection
- User creation
- Login/registration endpoints
- CORS configuration

## Full Test Suite

### 1. Unit Tests (In-Memory Database)
```bash
cd backend
python test_auth.py
```

Tests:
- ✓ Successful login
- ✓ Invalid credentials
- ✓ Missing fields
- ✓ Successful registration
- ✓ Duplicate username/email
- ✓ Session persistence

### 2. Integration Tests (Requires Running Server)
```bash
# In one terminal, start the server:
cd backend
source venv/bin/activate
python app.py

# In another terminal, run:
cd backend
python test_real_server.py
```

This tests against the actual running server with real HTTP requests.

### 3. Diagnostic Test
```bash
cd backend
python test_diagnostic.py
```

Comprehensive diagnostic that identifies specific issues.

## Test Results

**All backend tests PASS** ✅

This means:
- Registration endpoint works correctly
- Login endpoint works correctly  
- Session cookies work correctly
- Password hashing works correctly

## If Tests Pass But Browser Still Fails

The issue is likely:

1. **Browser Cookie Problems**
   - Solution: Clear cookies and restart browser

2. **Wrong Credentials**
   - Solution: Use `testuser` / `testpass123` or register new account

3. **CORS/Cookie Issues**
   - Solution: Check browser console for CORS errors
   - Make sure frontend is on port 3001 and backend on 5001

4. **Backend Not Running**
   - Solution: Check backend is running on port 5001

## Create Test User

```bash
cd backend
python create_test_user.py
```

Creates user: `testuser` / `testpass123`

