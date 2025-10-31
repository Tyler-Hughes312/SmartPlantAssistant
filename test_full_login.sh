#!/bin/bash
echo "=== FULL LOGIN TEST ==="
echo ""
echo "Step 1: Checking test user..."
cd backend
python3 -c "
from app import app, db, User
from werkzeug.security import check_password_hash
with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        is_valid = check_password_hash(user.password_hash, 'testpass123')
        print(f'✓ User exists: {user.username}')
        print(f'✓ Password valid: {is_valid}')
    else:
        print('✗ User not found!')
"
echo ""
echo "Step 2: Backend should be running on port 5001"
echo "Check: curl http://localhost:5001/api/health"
echo ""
echo "Step 3: Test login (if backend is running):"
echo "cd backend && python3 test_login_direct.py"
