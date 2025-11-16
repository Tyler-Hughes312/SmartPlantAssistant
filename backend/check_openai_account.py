#!/usr/bin/env python3
"""
Check OpenAI account details to verify API key matches account
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

api_key = os.environ.get('OPENAI_API_KEY')

if not api_key:
    print('❌ ERROR: OPENAI_API_KEY not found')
    sys.exit(1)

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print('🔍 Checking OpenAI account information...\n')
    
    # Try to get account info (this might not work with all API keys)
    try:
        # List models to verify key works
        print('📋 Fetching available models...')
        models = client.models.list()
        print(f'✅ API key is valid! Found {len(list(models.data))} models available.\n')
        
        # Try to get organization info
        print('🔑 API Key Details:')
        print(f'   Key starts with: {api_key[:7]}...{api_key[-4:]}')
        print(f'   Key length: {len(api_key)} characters')
        
        # Check if we can make a simple request
        print('\n🧪 Testing with cheapest model (gpt-3.5-turbo)...')
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'test'"}],
                max_tokens=5
            )
            print('✅ SUCCESS! API is working correctly!')
            print(f'   Response: {response.choices[0].message.content}')
        except Exception as e:
            error_str = str(e)
            print(f'❌ Error: {error_str}')
            
            if 'quota' in error_str.lower() or 'insufficient_quota' in error_str:
                print('\n⚠️  QUOTA ISSUE DETECTED')
                print('   Even though you see $5 available, the API is reporting quota issues.')
                print('\n   Possible causes:')
                print('   1. API key belongs to a different account than the one you\'re checking')
                print('   2. Account needs payment method verification')
                print('   3. Account needs activation (check email for verification)')
                print('   4. Billing limits or restrictions are set')
                print('\n   🔧 SOLUTIONS:')
                print('   - Verify the API key matches the account at: https://platform.openai.com/api-keys')
                print('   - Check billing settings: https://platform.openai.com/account/billing')
                print('   - Ensure payment method is verified')
                print('   - Check for any spending limits: https://platform.openai.com/account/billing/limits')
                print('   - Try creating a new API key: https://platform.openai.com/api-keys')
                
    except Exception as e:
        print(f'❌ Error accessing account: {e}')
        print('\n   This might indicate:')
        print('   - API key is invalid or expired')
        print('   - Account access issues')
        print('   - Network connectivity problems')
        
except ImportError:
    print('❌ ERROR: openai package not installed')
    print('   Install with: pip install openai')
    sys.exit(1)

