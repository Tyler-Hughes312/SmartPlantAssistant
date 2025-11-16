#!/usr/bin/env python3
"""
Test the chat endpoint's OpenAI integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables (same way as app.py)
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f'✅ Loaded environment variables from {env_path}')
else:
    print(f'⚠️  .env file not found at {env_path}')

# Get API key (same way as app.py)
api_key = os.environ.get('OPENAI_API_KEY')

if not api_key:
    print('❌ ERROR: OPENAI_API_KEY not found in environment')
    sys.exit(1)

print(f'✅ Found OpenAI API key (starts with: {api_key[:7]}...)')

# Test OpenAI connection exactly as the backend does
try:
    from openai import OpenAI
    
    print('\n🧪 Testing OpenAI connection (same way as backend chat endpoint)...')
    client = OpenAI(api_key=api_key)
    
    # Try models in the same order as backend
    models_to_try = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
    completion = None
    model_used = None
    
    for model_name in models_to_try:
        try:
            print(f'   Trying {model_name}...')
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful plant care assistant."},
                    {"role": "user", "content": "Say 'Chat endpoint is ready!' and nothing else."}
                ],
                temperature=0.7
            )
            model_used = model_name
            print(f'   ✅ Success with {model_name}!')
            break
        except Exception as e:
            error_str = str(e)
            if 'model_not_found' in error_str or 'does not exist' in error_str:
                print(f'   ⚠️  {model_name} not available, trying next...')
                continue
            else:
                raise
    
    if not completion:
        print('❌ ERROR: No models available')
        sys.exit(1)
    
    message = completion.choices[0].message.content
    print(f'\n✅ SUCCESS! Chat endpoint will work correctly!')
    print(f'   Model that will be used: {model_used}')
    print(f'   Test response: {message}')
    print(f'\n🎉 Your chatbot is ready to use!')
    print(f'   The backend will automatically use: {model_used}')
    
except Exception as e:
    error_str = str(e)
    print(f'\n❌ ERROR: {error_str}')
    
    if 'quota' in error_str.lower():
        print('   ⚠️  Quota issue - check billing')
    elif 'rate_limit' in error_str.lower():
        print('   ⚠️  Rate limit - wait a moment')
    else:
        print('   ⚠️  Unexpected error')
    
    sys.exit(1)

