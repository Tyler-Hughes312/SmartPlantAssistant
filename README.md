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
- OpenAI API key (optional, for chatbot functionality)

### Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # OpenAI API Key for chatbot functionality (optional)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # NWS (National Weather Service) API User-Agent
   # Format: AppName-your.email@domain.com
   NWS_USER_AGENT=SmartPlantAssistant-your.email@example.com
   
   # Flask Secret Key (auto-generated if not set)
   # SECRET_KEY=your_secret_key_here
   
   # Database URL (defaults to SQLite if not set)
   # DATABASE_URL=sqlite:///smart_plant.db
   ```

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

4. Run the Flask server:
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

## Integrating Your Sensors

To connect your actual sensors, you have two options:

1. **Update sensor data via API**: Modify your sensor code to POST data to `/api/sensor-data` endpoint
2. **Modify backend**: Update the `get_sensor_data()` function in `app.py` to fetch from your sensor's API or device

Example POST to update sensor data:
```bash
curl -X POST http://localhost:5000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d '{"light": 450, "moisture": 50, "temperature": 75}'
```

## Technologies

- **Backend**: Flask, Python, NumPy, SQLAlchemy, Flask-Login
- **Frontend**: React, Chart.js, Axios
- **ML**: Custom neural network model for predictions
- **APIs**: National Weather Service API, OpenAI API (optional)
- **Database**: SQLite (configurable via DATABASE_URL)
- **Authentication**: Session-based with Flask-Login

## Browser Compatibility

Works in all modern browsers that support:
- ES6 JavaScript
- Fetch API
- Geolocation API
- Canvas API (for charts)

## Development Notes

- The backend uses CORS to allow React frontend to communicate
- Sensor data is currently simulated but can be easily replaced with real sensor readings
- Weather data is fetched based on user's geolocation (with fallback to default location)
- Predictions update every 5 seconds along with sensor data

## Security Notes

- Never commit your `.env` file to version control
- The `.env.example` file shows the required environment variables without sensitive data
- Database files (`.db`) are excluded from version control
- Generate a strong SECRET_KEY for production deployments

## License

[Add your license here]

## Contributing

[Add contributing guidelines if applicable]
