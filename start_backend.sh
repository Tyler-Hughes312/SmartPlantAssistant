#!/bin/bash

# Start Flask backend server
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt --quiet
python app.py

