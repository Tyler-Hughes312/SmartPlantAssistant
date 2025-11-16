#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is working
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
    print(f'✅ Loaded environment variables from {env_path}')
else:
    print(f'⚠️  .env file not found at {env_path}')
    print('   Using system environment variables only.')

# Get API key
api_key = os.environ.get('OPENAI_API_KEY')

if not api_key:
    print('❌ ERROR: OPENAI_API_KEY not found in environment variables')
    print('   Please set it in your .env file:')
    print('   OPENAI_API_KEY=sk-...')
    sys.exit(1)

# Check if key looks valid (starts with sk-)
if not api_key.startswith('sk-'):
    print(f'⚠️  WARNING: API key does not start with "sk-"')
    print(f'   Key starts with: {api_key[:5]}...')

print(f'✅ Found OpenAI API key (starts with: {api_key[:7]}...)')

# Test OpenAI connection
try:
    from openai import OpenAI
    
    print('\n🔄 Testing OpenAI API connection...')
    client = OpenAI(api_key=api_key)
    
    # Try different models - start with cheapest first
    models_to_try = [
        "gpt-3.5-turbo",  # Cheapest, try first
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4"
    ]
    
    response = None
    model_used = None
    
    for model_name in models_to_try:
        try:
            print(f'   Trying model: {model_name}...')
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, OpenAI API is working!' and nothing else."}
                ],
                max_tokens=50,
                temperature=0.7
            )
            model_used = model_name
            print(f'   ✅ Success with {model_name}!')
            break
        except Exception as e:
            if 'model_not_found' in str(e) or 'does not exist' in str(e):
                print(f'   ⚠️  {model_name} not available, trying next...')
                continue
            else:
                raise
    
    if not response:
        print('❌ ERROR: None of the tested models are available')
        print('   Available models may be limited for your account')
        sys.exit(1)
    
    message = response.choices[0].message.content
    print(f'✅ OpenAI API is working!')
    print(f'   Model used: {model_used}')
    print(f'   Response: {message}')
    print(f'\n✅ SUCCESS: Your OpenAI API key is valid and responding correctly!')
    print(f'   Recommended model for backend: {model_used}')
    
except ImportError:
    print('❌ ERROR: openai package not installed')
    print('   Install with: pip install openai')
    sys.exit(1)
    
except Exception as e:
    error_msg = str(e)
    print(f'\n❌ ERROR: OpenAI API test failed')
    print(f'   Error: {error_msg}')
    
    # Check for common errors
    if 'Invalid API key' in error_msg or 'Incorrect API key' in error_msg:
        print('\n   🔧 SOLUTION: Your API key is invalid or incorrect.')
        print('   - Check that your API key is correct in .env file')
        print('   - Make sure there are no extra spaces or quotes')
        print('   - Get a new key from: https://platform.openai.com/api-keys')
    elif 'Rate limit' in error_msg or 'quota' in error_msg.lower():
        print('\n   🔧 SOLUTION: You have hit a rate limit or exceeded your quota.')
        print('   - Check your OpenAI account billing and usage')
        print('   - Visit: https://platform.openai.com/usage')
    elif 'model' in error_msg.lower() and 'not found' in error_msg.lower():
        print('\n   🔧 SOLUTION: GPT-4 model may not be available for your account.')
        print('   - Check your OpenAI account tier')
        print('   - You may need to upgrade or use gpt-3.5-turbo instead')
    else:
        print('\n   🔧 TROUBLESHOOTING:')
        print('   - Check your internet connection')
        print('   - Verify your OpenAI account is active')
        print('   - Check OpenAI status: https://status.openai.com/')
    
    sys.exit(1)

