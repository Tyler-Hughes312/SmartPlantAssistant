# Chatbot Setup Guide

The Smart Plant Assistant includes an AI-powered chatbot using AutoGen and OpenAI.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

This will install:
- `openai` - OpenAI API client
- `pyautogen` - AutoGen framework for AI agents

### 2. Set Your OpenAI API Key

You have two options:

#### Option A: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY="your-api-key-here"
```

To make it permanent, add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Option B: Create a `.env` file (Alternative)
Create `backend/.env`:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Restart the Flask Backend

After setting the API key, restart your Flask server:
```bash
# Stop current server (Ctrl+C or):
pkill -f "python.*app.py"

# Start again:
cd backend && source venv/bin/activate && python app.py
```

## How It Works

- The chatbot appears at the bottom of the dashboard
- It has access to:
  - Current sensor readings (moisture, temperature, light)
  - Weather data from NWS
  - Plant health score and status
  - Plant name and information

- The chatbot can:
  - Answer questions about plant care
  - Provide recommendations based on current conditions
  - Explain sensor readings
  - Give watering advice

## Testing

Once configured, try asking:
- "What's my plant's current health?"
- "Should I water my plant?"
- "What do my sensor readings mean?"
- "How can I improve my plant's health?"

## Troubleshooting

**Error: "OpenAI API key not configured"**
- Make sure you've set the `OPENAI_API_KEY` environment variable
- Restart the Flask server after setting it

**Error: "AutoGen not installed"**
- Run: `pip install pyautogen openai`

**Chatbot not responding**
- Check Flask server logs for errors
- Verify your API key is valid and has credits
- Ensure AutoGen is installed correctly

