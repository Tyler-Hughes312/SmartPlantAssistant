#!/usr/bin/env python3
"""
Training script for the Random Forest watering prediction model.

This script:
1. Generates synthetic training data (or loads from database)
2. Trains the Random Forest model
3. Saves the trained model to disk
4. Evaluates model performance
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_model import WateringPredictionModel, generate_synthetic_training_data
import numpy as np


def load_training_data_from_db():
    """
    Load training data from the database.
    
    This extracts historical sensor readings and calculates target values
    based on moisture trends.
    
    Returns:
        tuple: (X, y) feature matrix and target vector, or (None, None) if insufficient data
    """
    try:
        from app import app, db, SensorReading, Plant
        
        with app.app_context():
            # Get all sensor readings
            readings = SensorReading.query.order_by(SensorReading.timestamp).all()
            
            if len(readings) < 20:
                print(f"Only {len(readings)} readings in database. Need at least 20 for training.")
                return None, None
            
            X = []
            y = []
            
            # Group readings by plant
            plant_readings = {}
            for reading in readings:
                if reading.plant_id not in plant_readings:
                    plant_readings[reading.plant_id] = []
                plant_readings[reading.plant_id].append(reading)
            
            # For each plant, calculate time until watering threshold
            for plant_id, readings_list in plant_readings.items():
                # Sort by timestamp
                readings_list.sort(key=lambda r: r.timestamp)
                
                # Find when moisture drops below threshold (30%)
                for i in range(len(readings_list) - 1):
                    current = readings_list[i]
                    next_reading = readings_list[i + 1]
                    
                    # If moisture drops below 30%, calculate hours until that point
                    if current.moisture > 30 and next_reading.moisture <= 30:
                        hours_diff = (next_reading.timestamp - current.timestamp).total_seconds() / 3600
                        
                        if 6 <= hours_diff <= 168:  # Reasonable range
                            # We need weather data, but we don't store it
                            # Use synthetic weather data for now
                            # In production, you'd store weather data with readings
                            X.append([
                                current.moisture,
                                current.temperature,
                                60,  # Default humidity (would need to fetch from weather API)
                                0    # Default precipitation
                            ])
                            y.append(hours_diff)
            
            if len(X) < 10:
                print(f"Only {len(X)} valid training samples from database.")
                return None, None
            
            return np.array(X), np.array(y)
    except ImportError:
        print("Flask dependencies not available. Skipping database loading.")
        return None, None
    except Exception as e:
        print(f"Error loading from database: {e}")
        return None, None


def main():
    """Main training function."""
    print("="*70)
    print("RANDOM FOREST MODEL TRAINING")
    print("="*70)
    
    # Generate weather-only training data (no moisture sensor available)
    print("\n1. Generating training data...")
    print("   Using weather-only model (temperature, humidity, precipitation)")
    print("   No moisture sensor data available - using evapotranspiration-based predictions")
    
    X, y = generate_synthetic_training_data(n_samples=500, include_moisture=False)
    print(f"   Generated {len(X)} synthetic training samples based on weather conditions")
    
    # Initialize model
    print("\n2. Initializing model...")
    model = WateringPredictionModel()
    
    # Train model
    print("\n3. Training model...")
    metrics = model.train(X, y, test_size=0.2, verbose=True)
    
    # Show feature importance
    print("\n4. Feature Importance:")
    importance = model.get_feature_importance()
    if importance:
        for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"   {feature:15s}: {score:.3f}")
    
    # Test predictions
    print("\n5. Sample Predictions (Weather-Only):")
    test_cases = [
        ([75, 50, 0], "Warm, moderate humidity, no rain"),
        ([70, 60, 20], "Moderate temp, good humidity, some rain"),
        ([80, 40, 0], "Hot, low humidity, no rain (high evaporation)"),
        ([65, 70, 0], "Cool, high humidity, no rain (low evaporation)"),
        ([85, 30, 10], "Very hot, very dry, light rain"),
    ]
    
    for features, description in test_cases:
        pred = model.predict(features)
        print(f"   {description}")
        print(f"   Features: temp={features[0]}°F, humidity={features[1]}%, precip={features[2]}%")
        print(f"   Prediction: {pred:.1f} hours until watering\n")
    
    print("="*70)
    print("TRAINING COMPLETE!")
    print(f"Model saved to: {model.model_path}")
    print("="*70)


if __name__ == '__main__':
    main()

