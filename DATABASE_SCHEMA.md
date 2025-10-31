# Database Schema

This document describes the database schema for the Smart Plant Assistant application.

## Overview

The application uses SQLite (default) or PostgreSQL (production) with SQLAlchemy ORM. The database consists of three main tables: `users`, `plants`, and `sensor_readings`.

## Tables

### Users Table (`users`)

Stores user account information and authentication credentials.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique user identifier |
| `username` | String(80) | Unique, Not Null | User's username for login |
| `email` | String(120) | Unique, Not Null | User's email address |
| `password_hash` | String(255) | Not Null | Hashed password (using Werkzeug) |
| `location` | String(200) | Default: 'New York, NY' | User's location (city/place name) |
| `latitude` | Float | Default: 40.7128 | Latitude coordinate for weather data |
| `longitude` | Float | Default: -74.0060 | Longitude coordinate for weather data |
| `created_at` | DateTime | Default: UTC now | Account creation timestamp |

**Relationships:**
- One-to-Many with `plants` (a user can have multiple plants)

---

### Plants Table (`plants`)

Stores information about each plant/sensor pair linked to a user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique plant identifier |
| `name` | String(100) | Not Null | User-friendly plant name (e.g., "Basil", "Tomato") |
| `user_id` | Integer | Foreign Key → `users.id`, Not Null | Owner of this plant |
| `sensor_id` | String(100) | Unique, Not Null | Unique sensor identifier/hardware ID |
| `created_at` | DateTime | Default: UTC now | Plant registration timestamp |

**Relationships:**
- Many-to-One with `users` (each plant belongs to one user)
- One-to-Many with `sensor_readings` (each plant has many readings)

**Indexes:**
- Unique constraint on `sensor_id` (prevents duplicate sensor assignments)

---

### Sensor Readings Table (`sensor_readings`)

Stores historical sensor data readings for each plant.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique reading identifier |
| `plant_id` | Integer | Foreign Key → `plants.id`, Not Null | Plant this reading belongs to |
| `light` | Float | Not Null | Light level in lux |
| `moisture` | Float | Not Null | Soil moisture percentage (0-100) |
| `temperature` | Float | Not Null | Temperature in Fahrenheit |
| `timestamp` | DateTime | Not Null, Default: UTC now | When the reading was taken |

**Relationships:**
- Many-to-One with `plants` (each reading belongs to one plant)

---

## Entity Relationship Diagram

```
┌─────────────┐
│    Users    │
├─────────────┤
│ id (PK)     │
│ username    │◄────────┐
│ email       │         │
│ password_   │         │
│   hash      │         │
│ created_at  │         │
└─────────────┘         │
       │                │
       │ 1               │ Many
       │                │
       │ has many       │
       │                │
       ▼                │
┌─────────────┐         │
│   Plants    │─────────┘
├─────────────┤
│ id (PK)     │
│ name        │◄────────┐
│ user_id(FK) │         │
│ sensor_id   │         │
│ created_at  │         │
└─────────────┘         │
       │                │
       │ 1               │ Many
       │                │
       │ has many       │
       │                │
       ▼                │
┌─────────────────┐     │
│ Sensor Readings │─────┘
├─────────────────┤
│ id (PK)         │
│ plant_id (FK)   │
│ light           │
│ moisture        │
│ temperature     │
│ timestamp       │
└─────────────────┘
```

## Code Reference

The schema is defined in `backend/app.py`:

```python
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
    sensor_id = db.Column(db.String(100), unique=True, nullable=False)
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
```

## Database Initialization

The database is automatically created on first run in `backend/app.py`:

```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
```

The database file (SQLite) will be created at: `backend/smart_plant.db`

## Data Flow

1. **User Registration/Login**: Creates/authenticates user in `users` table
2. **Plant Creation**: User creates a plant linked to a sensor_id in `plants` table
3. **Sensor Data**: Sensor readings are posted to `sensor_readings` table via `/api/sensor-data` endpoint
4. **Data Retrieval**: Sensor data is filtered by `user_id` → `plant_id` to ensure users only see their own data

## Security Considerations

- Passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2)
- All API endpoints (except `/api/register`, `/api/login`) require authentication via Flask-Login sessions
- Data access is filtered by `user_id` to prevent cross-user data access
- Cascade deletes: Deleting a user deletes all their plants; deleting a plant deletes all its readings

