from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import numpy as np
from datetime import datetime, timezone
import os
import secrets
# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    # Look for .env in the project root (parent of backend directory)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f'Loaded environment variables from {env_path}')
    else:
        print(f'.env file not found at {env_path}, using system environment variables')
except ImportError:
    print('python-dotenv not installed. Install with: pip install python-dotenv')
    print('Using system environment variables only.')

app = Flask(__name__)
# SECRET_KEY must be consistent across app restarts for sessions to work
# If not set in .env, use a fixed development key (change in production!)
SECRET_KEY_ENV = os.environ.get('SECRET_KEY')
if SECRET_KEY_ENV:
    app.config['SECRET_KEY'] = SECRET_KEY_ENV
else:
    # Fixed dev key - sessions will persist across restarts
    # IMPORTANT: Set SECRET_KEY in .env for production!
    app.config['SECRET_KEY'] = 'dev-secret-key-fixed-for-sessions-please-change-in-production-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///smart_plant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
# For localhost cross-port, use 'None' with Secure=False (development only)
# Browsers treat localhost as same-site, but explicit setting helps
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 'Lax' works for localhost cross-port
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_DOMAIN'] = None  # None allows cookies for localhost
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_NAME'] = 'session'  # Explicit cookie name
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Enable CORS with credentials for session cookies
CORS(app, 
     supports_credentials=True, 
     origins=['http://localhost:3000', 'http://localhost:3001'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     expose_headers=['Set-Cookie'],
     allow_credentials=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None  # Don't redirect for API

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access - return 401 for API"""
    return jsonify({'error': 'Authentication required'}), 401

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(200), default='New York, NY')  # City/Place name
    latitude = db.Column(db.Float, default=40.7128)  # Default to NYC
    longitude = db.Column(db.Float, default=-74.0060)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    plants = db.relationship('Plant', backref='owner', lazy=True, cascade='all, delete-orphan')

class Plant(db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sensor_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique sensor identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sensor_readings = db.relationship('SensorReading', backref='plant', lazy=True, cascade='all, delete-orphan')

class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    light = db.Column(db.Float, nullable=False)
    moisture = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    """Load user from database for Flask-Login"""
    try:
        user = db.session.get(User, int(user_id))
        print(f'DEBUG load_user: Loading user_id={user_id}, found={user is not None}')
        return user
    except (ValueError, TypeError) as e:
        print(f'DEBUG load_user: Error loading user_id={user_id}: {e}')
        return None
    except Exception as e:
        print(f'DEBUG load_user: Unexpected error loading user_id={user_id}: {e}')
        return None

# ML Model
class WateringPredictionModel:
    def __init__(self):
        self.weights = np.array([
            [-0.3, -0.8, -0.2, -0.1, 0.4, -0.15, -0.5],
        ])
        self.bias = 0.6
    
    def predict(self, features):
        features_array = np.array(features).reshape(1, -1)
        normalized = np.array([
            features_array[0][0] / 100,
            features_array[0][1] / 100,
            features_array[0][2] / 1000,
            features_array[0][3] / 100,
            features_array[0][4] / 100,
            features_array[0][5] / 20,
            features_array[0][6] / 10
        ])
        prediction = np.dot(normalized, self.weights[0]) + self.bias
        prediction = 1 / (1 + np.exp(-prediction))
        return float(prediction)

ml_model = WateringPredictionModel()

# NWS API User-Agent (required for API access)
NWS_USER_AGENT = os.environ.get('NWS_USER_AGENT', 'SmartPlantAssistant-tyler.i.hughes@vanderbilt.edu')
NWS_HEADERS = {'User-Agent': NWS_USER_AGENT}

# Authentication Routes
def geocode_location(location_name):
    """Convert a place name to latitude/longitude using Nominatim (OpenStreetMap)"""
    try:
        if not location_name or not location_name.strip():
            return None, None
        
        # Use Nominatim geocoding service (free, no API key needed)
        geocode_url = 'https://nominatim.openstreetmap.org/search'
        params = {
            'q': location_name,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': NWS_USER_AGENT  # Respectful use of free service
        }
        
        response = requests.get(geocode_url, params=params, headers=headers, timeout=10)
        
        if response.ok:
            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                lat = float(result.get('lat', 0))
                lon = float(result.get('lon', 0))
                return lat, lon
        
        return None, None
    except Exception as e:
        print(f'Geocoding error: {e}')
        return None, None

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        location = data.get('location')  # Place name (e.g., "Nashville, TN")
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Handle location - prefer place name, fallback to coordinates, then default
        if location and location.strip():
            # Geocode the place name
            lat, lon = geocode_location(location)
            if lat and lon:
                latitude = lat
                longitude = lon
            else:
                return jsonify({'error': f'Could not find location: {location}. Please try a more specific location (e.g., "City, State" or "City, Country")'}), 400
        elif latitude is not None and longitude is not None:
            # Use provided coordinates
            latitude = float(latitude)
            longitude = float(longitude)
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return jsonify({'error': 'Invalid coordinates'}), 400
            location = f"{latitude:.4f}, {longitude:.4f}"  # Create a simple location string
        else:
            # Default to NYC if nothing provided
            location = 'New York, NY'
            latitude = 40.7128
            longitude = -74.0060

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            location=location,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(user)
        db.session.commit()

        # Login the user immediately after registration
        login_user(user, remember=True)
        session.permanent = True  # Make session persistent
        
        response = jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'location': user.location,
                'latitude': user.latitude,
                'longitude': user.longitude
            }
        })
        
        print(f'DEBUG register: Registered user {user.id}, session keys={list(session.keys())}')
        print(f'DEBUG register: _user_id in session={session.get("_user_id")}')
        
        return response, 201

    except ValueError as e:
        print(f'Registration ValueError: {e}')
        return jsonify({'error': 'Invalid location or coordinates'}), 400
    except Exception as e:
        db.session.rollback()
        print(f'Registration error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            # Ensure session is saved and persistent
            session.permanent = True
            
            print(f'DEBUG login: Logged in user {user.id}, session keys={list(session.keys())}')
            print(f'DEBUG login: _user_id in session={session.get("_user_id")}')
            
            # Build user response safely (handle None values)
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email or '',
                'location': getattr(user, 'location', None) or '',
                'latitude': getattr(user, 'latitude', None),
                'longitude': getattr(user, 'longitude', None)
            }
            
            # Convert None to None (JSON null), but ensure numeric types
            if user_data['latitude'] is None:
                user_data['latitude'] = None
            if user_data['longitude'] is None:
                user_data['longitude'] = None
            
            response = jsonify({
                'message': 'Login successful',
                'user': user_data
            })
            
            # Explicitly set cookie attributes to ensure they're sent
            print(f'DEBUG login: Response headers before: {list(response.headers.keys())}')
            
            return response
        else:
            print(f'DEBUG login: Invalid credentials for username: {username}')
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        print(f'Login error [{error_type}]: {error_message}')
        import traceback
        print('=' * 70)
        print('FULL TRACEBACK:')
        traceback.print_exc()
        print('=' * 70)
        return jsonify({
            'error': 'Login failed',
            'error_type': error_type,
            'details': error_message
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session status"""
    return jsonify({
        'session_keys': list(session.keys()),
        'user_id': session.get('_user_id'),
        'permanent': session.permanent,
        'is_authenticated': current_user.is_authenticated if current_user else False,
        'user': {
            'id': current_user.id,
            'username': current_user.username
        } if current_user and current_user.is_authenticated else None,
        'cookies_received': list(request.cookies.keys())
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/user', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged in user"""
    try:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email or '',
            'location': getattr(current_user, 'location', None) or '',
            'latitude': getattr(current_user, 'latitude', None),
            'longitude': getattr(current_user, 'longitude', None)
        })
    except Exception as e:
        print(f'Error in get_current_user: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get user data', 'details': str(e)}), 500

@app.route('/api/user/location', methods=['PUT'])
@login_required
def update_user_location():
    """Update user's location by place name or coordinates"""
    try:
        data = request.json
        location = data.get('location')  # Place name
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Prefer place name over coordinates
        if location and location.strip():
            lat, lon = geocode_location(location)
            if lat and lon:
                current_user.location = location
                current_user.latitude = lat
                current_user.longitude = lon
                db.session.commit()
                
                return jsonify({
                    'message': 'Location updated successfully',
                    'location': current_user.location,
                    'latitude': current_user.latitude,
                    'longitude': current_user.longitude
                })
            else:
                return jsonify({'error': f'Could not find location: {location}. Please try a more specific location.'}), 400
        
        # Fallback to coordinates if provided
        elif latitude is not None and longitude is not None:
            latitude = float(latitude)
            longitude = float(longitude)
            
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return jsonify({'error': 'Invalid coordinates'}), 400
            
            current_user.latitude = latitude
            current_user.longitude = longitude
            current_user.location = f"{latitude:.4f}, {longitude:.4f}"
            db.session.commit()
            
            return jsonify({
                'message': 'Location updated successfully',
                'location': current_user.location,
                'latitude': current_user.latitude,
                'longitude': current_user.longitude
            })
        else:
            return jsonify({'error': 'Location name or coordinates are required'}), 400
            
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Plant Management Routes
@app.route('/api/plants', methods=['GET'])
@login_required
def get_plants():
    """Get all plants for current user"""
    plants = Plant.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': plant.id,
        'name': plant.name,
        'sensor_id': plant.sensor_id,
        'created_at': plant.created_at.isoformat()
    } for plant in plants])

@app.route('/api/plants', methods=['POST'])
@login_required
def create_plant():
    """Create a new plant"""
    try:
        # Debug: Check authentication status
        print(f'DEBUG create_plant: current_user={current_user}, is_authenticated={current_user.is_authenticated if current_user else False}')
        print(f'DEBUG create_plant: cookies={dict(request.cookies)}')
        print(f'DEBUG create_plant: session={dict(session)}')
        
        data = request.json
        name = data.get('name')
        sensor_id = data.get('sensor_id')

        if not name or not sensor_id:
            return jsonify({'error': 'Name and sensor_id required'}), 400

        if Plant.query.filter_by(sensor_id=sensor_id).first():
            return jsonify({'error': 'Sensor ID already in use'}), 400

        plant = Plant(
            name=name,
            sensor_id=sensor_id,
            user_id=current_user.id
        )
        db.session.add(plant)
        db.session.commit()

        return jsonify({
            'id': plant.id,
            'name': plant.name,
            'sensor_id': plant.sensor_id,
            'created_at': plant.created_at.isoformat()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f'Create plant error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
@login_required
def delete_plant(plant_id):
    """Delete a plant"""
    plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404

    db.session.delete(plant)
    db.session.commit()
    return jsonify({'message': 'Plant deleted successfully'})

# Sensor Data Routes
@app.route('/api/sensor-data', methods=['GET'])
@login_required
def get_sensor_data():
    """Get current sensor data for user's plants"""
    plant_id = request.args.get('plant_id', type=int)
    
    if plant_id:
        # Get specific plant's data
        plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
        if not plant:
            return jsonify({'error': 'Plant not found'}), 404
        
        # Get latest reading or simulate
        latest_reading = SensorReading.query.filter_by(plant_id=plant_id)\
            .order_by(SensorReading.timestamp.desc()).first()
        
        if latest_reading:
            return jsonify({
                'plant_id': plant_id,
                'plant_name': plant.name,
                'light': latest_reading.light,
                'moisture': latest_reading.moisture,
                'temperature': latest_reading.temperature,
                'timestamp': latest_reading.timestamp.isoformat()
            })
        else:
            # Simulate data if no readings
            return jsonify(generate_simulated_data(plant_id, plant.name))
    else:
        # Get all plants' data
        plants = Plant.query.filter_by(user_id=current_user.id).all()
        if not plants:
            return jsonify({'error': 'No plants found. Please add a plant first.'}), 404
        
        # Return first plant's data by default
        plant = plants[0]
        latest_reading = SensorReading.query.filter_by(plant_id=plant.id)\
            .order_by(SensorReading.timestamp.desc()).first()
        
        if latest_reading:
            return jsonify({
                'plant_id': plant.id,
                'plant_name': plant.name,
                'light': latest_reading.light,
                'moisture': latest_reading.moisture,
                'temperature': latest_reading.temperature,
                'timestamp': latest_reading.timestamp.isoformat()
            })
        else:
            return jsonify(generate_simulated_data(plant.id, plant.name))

@app.route('/api/sensor-data', methods=['POST'])
@login_required
def update_sensor_data():
    """Update sensor data from actual sensor"""
    try:
        data = request.json
        sensor_id = data.get('sensor_id')
        plant_id = data.get('plant_id')
        
        # Find plant by sensor_id or plant_id
        if sensor_id:
            plant = Plant.query.filter_by(sensor_id=sensor_id, user_id=current_user.id).first()
        elif plant_id:
            plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
        else:
            return jsonify({'error': 'sensor_id or plant_id required'}), 400
        
        if not plant:
            return jsonify({'error': 'Plant not found'}), 404
        
        # Create new sensor reading
        reading = SensorReading(
            plant_id=plant.id,
            light=data.get('light', 0),
            moisture=data.get('moisture', 0),
            temperature=data.get('temperature', 0)
        )
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'plant_id': plant.id,
                'plant_name': plant.name,
                'light': reading.light,
                'moisture': reading.moisture,
                'temperature': reading.temperature,
                'timestamp': reading.timestamp.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor-data/history', methods=['GET'])
@login_required
def get_sensor_history():
    """Get sensor reading history"""
    plant_id = request.args.get('plant_id', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    if not plant_id:
        return jsonify({'error': 'plant_id required'}), 400
    
    plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404
    
    readings = SensorReading.query.filter_by(plant_id=plant_id)\
        .order_by(SensorReading.timestamp.desc()).limit(limit).all()
    
    return jsonify([{
        'light': r.light,
        'moisture': r.moisture,
        'temperature': r.temperature,
        'timestamp': r.timestamp.isoformat()
    } for r in reversed(readings)])

def generate_simulated_data(plant_id, plant_name):
    """Generate simulated sensor data"""
    import random
    import math
    
    current_hour = datetime.now().hour
    light_variation = math.sin((current_hour - 6) * math.pi / 12) * 300 + random.uniform(-25, 25)
    moisture_variation = random.uniform(-2, 1)
    temp_variation = math.sin((current_hour - 6) * math.pi / 12) * 8 + random.uniform(-2, 2)
    
    return {
        'plant_id': plant_id,
        'plant_name': plant_name,
        'light': max(0, 400 + light_variation),
        'moisture': max(0, min(100, 45 + moisture_variation)),
        'temperature': 72 + temp_variation,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/weather', methods=['GET'])
@login_required
def get_weather():
    """Fetch weather data from NWS API"""
    try:
        # Use user's saved location, or request params, or defaults
        lat = request.args.get('lat') or current_user.latitude or 40.7128
        lon = request.args.get('lon') or current_user.longitude or -74.0060
        lat = float(lat)
        lon = float(lon)
        
        grid_url = f'https://api.weather.gov/points/{lat},{lon}'
        grid_response = requests.get(grid_url, headers=NWS_HEADERS, timeout=10)
        
        if not grid_response.ok:
            raise Exception('Failed to get grid point')
        
        grid_data = grid_response.json()
        forecast_url = grid_data['properties']['forecast']
        
        forecast_response = requests.get(forecast_url, headers=NWS_HEADERS, timeout=10)
        if not forecast_response.ok:
            raise Exception('Failed to get forecast')
        
        forecast_data = forecast_response.json()
        current_period = forecast_data['properties']['periods'][0]
        
        observation_data = None
        try:
            observation_url = grid_data['properties']['observationStations']
            stations_response = requests.get(observation_url, headers=NWS_HEADERS, timeout=10)
            
            if stations_response.ok:
                stations_data = stations_response.json()
                if stations_data.get('features') and len(stations_data['features']) > 0:
                    station_id = stations_data['features'][0]['properties']['stationIdentifier']
                    obs_response = requests.get(
                        f'https://api.weather.gov/stations/{station_id}/observations/latest',
                        headers=NWS_HEADERS,
                        timeout=10
                    )
                    if obs_response.ok:
                        observation_data = obs_response.json()
        except Exception as e:
            print(f'Could not fetch observations: {e}')
        
        temp = current_period['temperature']  # This is already in Fahrenheit from forecast
        humidity = current_period.get('relativeHumidity', {}).get('value')  # Try forecast first
        
        # Get more accurate data from observations if available
        if observation_data and observation_data.get('properties'):
            props = observation_data['properties']
            if props.get('temperature') and props['temperature'].get('value'):
                # NWS observation temperature is in Celsius, convert to Fahrenheit
                temp_celsius = props['temperature']['value']
                if temp_celsius is not None:
                    temp = (temp_celsius * 9/5) + 32
            # Prefer observation humidity if available
            if props.get('relativeHumidity') and props['relativeHumidity'].get('value') is not None:
                humidity = props['relativeHumidity']['value']
        
        # Fallback humidity if still not set
        if humidity is None:
            humidity = 60
        
        # Get wind speed - ALWAYS use forecast wind speed (not observation)
        # The forecast wind speed is in format like "5 to 10 mph" or "8 mph"
        forecast_wind_str = current_period.get('windSpeed', '5 mph')
        wind_speed = _parse_wind_speed(forecast_wind_str)
        
        print(f'[WEATHER] Using forecast wind: "{forecast_wind_str}" -> {wind_speed} mph')
        
        # Ignore observation wind speed - it can be inaccurate or from a different time
        
        weather = {
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'precipitation': current_period.get('probabilityOfPrecipitation', {}).get('value', 0),
            'windSpeed': round(wind_speed, 1),
            'forecast': current_period.get('shortForecast', 'Unknown'),
            'description': current_period.get('detailedForecast', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(weather)
        
    except Exception as e:
        print(f'Error fetching weather: {e}')
        # Fallback data - using reasonable defaults
        return jsonify({
            'temperature': 72,
            'humidity': 65,
            'precipitation': 0,
            'windSpeed': 8,
            'forecast': 'Partly Cloudy',
            'description': 'Weather data temporarily unavailable. Using default values.',
            'timestamp': datetime.now().isoformat(),
            'note': 'fallback_data'
        })

def _parse_wind_speed(wind_string):
    """Parse wind speed from NWS format (e.g., '5 to 10 mph', '5-10 mph', 'Calm', '8 mph')"""
    try:
        import re
        # Handle "Calm" or empty
        if not wind_string or wind_string.lower() in ['calm', 'none', '']:
            return 0.0
        
        # Convert to string if not already
        wind_str = str(wind_string).strip()
        
        # Extract numbers from string like "5 to 10 mph", "5-10 mph", or "8 mph"
        numbers = re.findall(r'\d+(?:\.\d+)?', wind_str)
        if numbers:
            # If range like "5 to 10" or "5-10", take the average
            if len(numbers) >= 2:
                avg = (float(numbers[0]) + float(numbers[1])) / 2
                print(f'Parsed wind range {wind_str} -> average: {avg} mph')
                return avg
            else:
                value = float(numbers[0])
                print(f'Parsed wind speed {wind_str} -> {value} mph')
                return value
    except Exception as e:
        print(f'Error parsing wind speed: {e}, string: {wind_string}')
    print(f'Using default wind speed 5.0 mph for: {wind_string}')
    return 5.0  # Default reasonable wind speed

@app.route('/api/predict', methods=['POST'])
@login_required
def predict_watering():
    """Predict when to water based on sensor and weather data"""
    try:
        data = request.json
        sensor = data.get('sensor', {})
        weather = data.get('weather', {})
        
        evapotranspiration = (
            sensor.get('temperature', 72) * 0.05 +
            weather.get('windSpeed', 5) * 0.1 -
            weather.get('humidity', 60) * 0.02
        )
        
        features = [
            sensor.get('moisture', 45),
            sensor.get('temperature', 72),
            sensor.get('light', 400),
            weather.get('humidity', 60),
            weather.get('precipitation', 0),
            weather.get('windSpeed', 5),
            evapotranspiration
        ]
        
        normalized_hours = ml_model.predict(features)
        hours = normalized_hours * 168
        hours = max(6, min(168, hours))
        
        confidence = abs(normalized_hours - 0.5) * 2
        confidence = max(0.5, confidence)
        
        return jsonify({
            'hoursUntilWatering': round(hours, 1),
            'confidence': round(confidence, 2),
            'recommendation': get_watering_recommendation(hours),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f'Prediction error: {e}')
        return jsonify({
            'error': str(e),
            'hoursUntilWatering': 72,
            'confidence': 0.7
        }), 500

def get_watering_recommendation(hours):
    """Get human-readable watering recommendation"""
    if hours < 24:
        return 'Water soon'
    elif hours < 48:
        return 'Water within 2 days'
    elif hours < 72:
        return 'Water within 3 days'
    else:
        return 'Watering not needed yet'

def calculate_plant_health_score(plant_id):
    """
    Calculate plant health score (0-100) based on sensor readings
    
    Formula Components:
    1. Moisture Score (0-30 points):
       - Optimal: 40-70% = 30 points
       - Good: 30-40% or 70-80% = 20 points
       - Fair: 20-30% or 80-90% = 10 points
       - Poor: <20% or >90% = 0 points
    
    2. Temperature Score (0-25 points):
       - Optimal: 65-80°F = 25 points
       - Good: 60-65°F or 80-85°F = 18 points
       - Fair: 55-60°F or 85-90°F = 10 points
       - Poor: <55°F or >90°F = 0 points
    
    3. Light Score (0-25 points):
       - Optimal: 300-800 lux = 25 points
       - Good: 200-300 lux or 800-1000 lux = 18 points
       - Fair: 100-200 lux or 1000-1500 lux = 10 points
       - Poor: <100 lux or >1500 lux = 0 points
    
    4. Trend Score (0-20 points):
       - Based on recent 5 readings
       - Stable/improving conditions = 20 points
       - Slight decline = 15 points
       - Moderate decline = 10 points
       - Rapid decline = 5 points
    
    Total Health Score = Moisture + Temperature + Light + Trend
    """
    # Get recent readings
    recent_readings = SensorReading.query.filter_by(plant_id=plant_id)\
        .order_by(SensorReading.timestamp.desc()).limit(5).all()
    
    if not recent_readings:
        return {
            'score': 50,  # Default if no data
            'status': 'Unknown',
            'details': {
                'moisture_score': 0,
                'temperature_score': 0,
                'light_score': 0,
                'trend_score': 10
            },
            'factors': ['No sensor data available']
        }
    
    latest = recent_readings[0]
    
    # 1. Moisture Score (0-30 points)
    moisture = latest.moisture
    if 40 <= moisture <= 70:
        moisture_score = 30
        moisture_status = 'optimal'
    elif 30 <= moisture < 40 or 70 < moisture <= 80:
        moisture_score = 20
        moisture_status = 'good'
    elif 20 <= moisture < 30 or 80 < moisture <= 90:
        moisture_score = 10
        moisture_status = 'fair'
    else:
        moisture_score = 0
        moisture_status = 'poor'
    
    # 2. Temperature Score (0-25 points)
    temp = latest.temperature
    if 65 <= temp <= 80:
        temp_score = 25
        temp_status = 'optimal'
    elif 60 <= temp < 65 or 80 < temp <= 85:
        temp_score = 18
        temp_status = 'good'
    elif 55 <= temp < 60 or 85 < temp <= 90:
        temp_score = 10
        temp_status = 'fair'
    else:
        temp_score = 0
        temp_status = 'poor'
    
    # 3. Light Score (0-25 points)
    light = latest.light
    if 300 <= light <= 800:
        light_score = 25
        light_status = 'optimal'
    elif 200 <= light < 300 or 800 < light <= 1000:
        light_score = 18
        light_status = 'good'
    elif 100 <= light < 200 or 1000 < light <= 1500:
        light_score = 10
        light_status = 'fair'
    else:
        light_score = 0
        light_status = 'poor'
    
    # 4. Trend Score (0-20 points) - Analyze recent trend
    trend_score = 20
    if len(recent_readings) >= 3:
        # Calculate average change rates
        moisture_changes = []
        temp_changes = []
        
        for i in range(len(recent_readings) - 1):
            prev = recent_readings[i + 1]
            curr = recent_readings[i]
            
            # Moisture declining is bad
            moisture_changes.append(curr.moisture - prev.moisture)
            # Temperature stability is good
            temp_changes.append(abs(curr.temperature - prev.temperature))
        
        avg_moisture_change = sum(moisture_changes) / len(moisture_changes)
        avg_temp_stability = 10 - (sum(temp_changes) / len(temp_changes))
        
        # Moisture declining rapidly
        if avg_moisture_change < -5:
            trend_score -= 10
        elif avg_moisture_change < -2:
            trend_score -= 5
        
        # Temperature unstable
        if avg_temp_stability < 5:
            trend_score -= 5
        
        trend_score = max(0, min(20, trend_score))
    
    # Calculate total score
    total_score = moisture_score + temp_score + light_score + trend_score
    total_score = max(0, min(100, total_score))
    
    # Determine status
    if total_score >= 80:
        status = 'Excellent'
    elif total_score >= 65:
        status = 'Good'
    elif total_score >= 50:
        status = 'Fair'
    elif total_score >= 30:
        status = 'Poor'
    else:
        status = 'Critical'
    
    # Generate factors/feedback
    factors = []
    if moisture_status == 'poor':
        factors.append('Soil moisture is too ' + ('low' if moisture < 20 else 'high'))
    elif moisture_status == 'fair':
        factors.append('Soil moisture is suboptimal')
    
    if temp_status == 'poor':
        factors.append('Temperature is too ' + ('low' if temp < 55 else 'high'))
    elif temp_status == 'fair':
        factors.append('Temperature is outside optimal range')
    
    if light_status == 'poor':
        factors.append('Light levels are too ' + ('low' if light < 100 else 'high'))
    elif light_status == 'fair':
        factors.append('Light levels are suboptimal')
    
    if trend_score < 15:
        factors.append('Recent readings show declining conditions')
    
    if not factors:
        factors.append('All conditions are optimal')
    
    return {
        'score': round(total_score, 1),
        'status': status,
        'details': {
            'moisture_score': round(moisture_score, 1),
            'temperature_score': round(temp_score, 1),
            'light_score': round(light_score, 1),
            'trend_score': round(trend_score, 1)
        },
        'factors': factors,
        'current_values': {
            'moisture': round(moisture, 1),
            'temperature': round(temp, 1),
            'light': round(light, 1)
        }
    }

@app.route('/api/plant-health/<int:plant_id>', methods=['GET'])
@login_required
def get_plant_health(plant_id):
    """Get plant health score for a specific plant"""
    plant = Plant.query.filter_by(id=plant_id, user_id=current_user.id).first()
    if not plant:
        return jsonify({'error': 'Plant not found'}), 404
    
    health = calculate_plant_health_score(plant_id)
    return jsonify(health)

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Chat endpoint using AutoGen with OpenAI"""
    try:
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', {})
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Import OpenAI (will be configured when API key is provided)
        try:
            import openai
            
            # Get API key from environment (user will set this later)
            api_key = os.environ.get('OPENAI_API_KEY')
            
            if not api_key:
                # Return helpful message if API key not set
                return jsonify({
                    'error': 'OpenAI API key not configured',
                    'message': 'Please set the OPENAI_API_KEY environment variable. The chatbot will be available once configured.',
                    'instructions': 'Set your OpenAI API key: export OPENAI_API_KEY=your_key_here'
                }), 503
            
            # Configure OpenAI
            openai.api_key = api_key
            
            # Create AutoGen agents
            config_list = [{
                'model': 'gpt-4',
                'api_key': api_key
            }]
            
            # Prepare context for the assistant
            context_info = f"""
Current Plant Information:
- Plant Name: {context.get('plantName', 'Unknown')}
- Health Score: {context.get('healthData', {}).get('score', 'N/A')}/100
- Health Status: {context.get('healthData', {}).get('status', 'Unknown')}

Current Sensor Readings:
- Soil Moisture: {context.get('sensorData', {}).get('moisture', 'N/A')}%
- Temperature: {context.get('sensorData', {}).get('temperature', 'N/A')}°F
- Light Level: {context.get('sensorData', {}).get('light', 'N/A')} lux

Current Weather:
- Temperature: {context.get('weatherData', {}).get('temperature', 'N/A')}°F
- Humidity: {context.get('weatherData', {}).get('humidity', 'N/A')}%
- Forecast: {context.get('weatherData', {}).get('forecast', 'N/A')}
"""
            
            # Use OpenAI directly with AutoGen wrapper for better compatibility
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            # Create system message with context
            system_message = f"""You are a helpful plant care assistant. You help users understand their plant's health, 
provide care recommendations, and answer questions about plant maintenance. Use the following context 
to provide personalized advice:

{context_info}

Be friendly, informative, and provide actionable advice based on the current sensor readings and health data."""
            
            # Call OpenAI API
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            
            # Extract response
            message_content = completion.choices[0].message.content
            
            return jsonify({
                'message': message_content,
                'timestamp': datetime.now().isoformat()
            })
            
        except ImportError:
            # Fallback if AutoGen not installed
            return jsonify({
                'error': 'AutoGen not installed',
                'message': 'Please install AutoGen: pip install pyautogen openai'
            }), 503
            
    except Exception as e:
        print(f'Chat error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Sorry, I encountered an error. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Initialize database
def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
