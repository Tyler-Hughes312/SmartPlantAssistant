# Smart Plant Assistant

A full-stack web application built with Flask (backend) and React (frontend) that monitors plant sensor data and uses machine learning to predict optimal watering times based on weather conditions.

## Features

- **User Authentication**: Secure login and registration with session-based authentication
- **Plant Management**: Add, select, and manage multiple plants with unique sensor IDs
- **Real-time Sensor Monitoring**: Displays Light, Soil Moisture, and Temperature data
- **National Weather Service Integration**: Fetches current weather data from the NWS API
- **ML-Powered Predictions**: Uses a trained model to predict when to water your plant based on:
  - Current soil moisture
  - Environmental conditions (temperature, light)
  - Weather forecast (humidity, precipitation, wind speed)
  - Evapotranspiration calculations
- **Plant Health Score**: Calculated health score based on sensor data with detailed breakdown
- **AI Chatbot**: OpenAI-powered chatbot for plant care advice (requires API key)
- **Data Visualization**: Interactive charts showing sensor data trends and watering predictions
- **Location Settings**: Set your location for accurate weather data
- **Modern UI**: Beautiful, responsive React interface with white theme

## Project Structure

```
SmartPlantAssistant/
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+ (backend)
- Node.js 14+ and npm (frontend)
- Neon Postgres database (free tier available at [neon.tech](https://neon.tech))
- OpenAI API key (optional, for chatbot functionality)

### Environment Variables

Create a `.env` file in the project root with the following:

```bash
# Neon Postgres Database URL (required)
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Flask Secret Key (required for sessions)
SECRET_KEY=your-secret-key-here

# NWS (National Weather Service) API User-Agent (required for weather)
# Format: AppName-your.email@domain.com
NWS_USER_AGENT=SmartPlantAssistant-your.email@example.com

# OpenAI API Key (optional, for chatbot functionality)
OPENAI_API_KEY=your_openai_api_key_here
```

**Important:** Never commit your `.env` file to version control. It's already in `.gitignore`.

### Backend Setup (Flask)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database (first time only):
   ```bash
   python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
   ```

5. Run the Flask server:
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5001` (port 5000 is often used by macOS AirPlay Receiver)

### Frontend Setup (React)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will run on `http://localhost:3001` and automatically proxy API requests to the backend.

### Quick Start (Both Services)

Use the provided start script:
```bash
./start.sh
```

This will start both the backend and frontend servers. To stop them:
```bash
./stop.sh
```

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user
- `GET /api/user` - Get current user information

### Sensor Data
- `GET /api/sensor-data` - Get current sensor readings for selected plant
- `POST /api/sensor-data` - Update sensor data (for actual sensor integration)

### Weather
- `GET /api/weather` - Get weather data from NWS API (uses user's saved location)
- `PUT /api/user/location` - Update user's location

### Plants
- `GET /api/plants` - Get all user's plants
- `POST /api/plants` - Create a new plant
- `PUT /api/plants/<id>` - Update a plant
- `DELETE /api/plants/<id>` - Delete a plant

### Predictions & Health
- `POST /api/predict` - Get watering prediction based on sensor and weather data
- `GET /api/plant-health/<plant_id>` - Get plant health score

### Chatbot
- `POST /api/chat` - Send message to AI chatbot (requires OpenAI API key)

## Raspberry Pi Sensor Integration

This project includes scripts for connecting Raspberry Pi sensors (AHT20, BH1750, Arduino I2C soil moisture) directly to the Neon database.

### Quick Setup

1. **SSH into your Raspberry Pi** and navigate to the project directory
2. **Install sensor dependencies**:
   ```bash
   pip3 install --user --break-system-packages psycopg2-binary python-dotenv adafruit-blinka adafruit-circuitpython-ahtx0 adafruit-circuitpython-bh1750 RPi.GPIO
   ```

3. **Set up environment variables** (create `~/.env` or use systemd service):
   ```bash
   DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   PLANT_ID=1
   ```

4. **Set up automatic readings** (every 10 seconds):
   ```bash
   cd raspberry_pi
   chmod +x setup_10_second_readings.sh
   sudo ./setup_10_second_readings.sh
   ```

5. **Check service status**:
   ```bash
   sudo systemctl status smart-plant-sensor.service
   ```

See `raspberry_pi/README.md` for detailed setup instructions and troubleshooting.

## Technologies

- **Backend**: Flask, Python, NumPy, SQLAlchemy, Flask-Login
- **Frontend**: React, Chart.js, Axios
- **ML**: Custom neural network model for predictions
- **APIs**: National Weather Service API, OpenAI API (optional)
- **Database**: Neon Postgres (cloud-hosted, accessible from Raspberry Pi and backend)
- **Authentication**: Session-based with Flask-Login

## Browser Compatibility

Works in all modern browsers that support:
- ES6 JavaScript
- Fetch API
- Geolocation API
- Canvas API (for charts)

## Development Notes

- The backend uses CORS to allow React frontend to communicate
- Sensor data comes from Raspberry Pi sensors connected to Neon Postgres database
- Weather data is fetched from NWS API based on user's saved location (must be set in Location Settings)
- Predictions update every 5 seconds along with sensor data
- All data displayed is real-time from physical sensors (no simulated data)

## Security Notes

- Never commit your `.env` file to version control
- The `.env.example` file shows the required environment variables without sensitive data
- Database files (`.db`) are excluded from version control
- Generate a strong SECRET_KEY for production deployments

## License

[Add your license here]

## Contributing

[Add contributing guidelines if applicable]
