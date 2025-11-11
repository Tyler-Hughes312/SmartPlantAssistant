"""
Training script for Plant Health Classifier

This script generates synthetic training data and trains the health classification model.
"""

import numpy as np
from health_model import PlantHealthClassifier


def generate_synthetic_health_data(n_samples=500):
    """
    Generate synthetic training data for health classification.
    
    Args:
        n_samples: Number of training samples to generate
    
    Returns:
        tuple: (X, y) where X is features and y is health scores (0-100)
    """
    np.random.seed(42)
    X = []
    y = []
    
    for _ in range(n_samples):
        # Generate realistic sensor readings
        moisture = np.random.uniform(10, 90)
        temp = np.random.uniform(55, 90)
        light = np.random.uniform(50, 1500)
        
        # Generate weather data
        weather_temp = np.random.uniform(60, 85)
        weather_humidity = np.random.uniform(30, 80)
        weather_precip = np.random.uniform(0, 50)
        
        # Generate historical readings for trends
        sensor_readings = [
            {
                'moisture': moisture + np.random.normal(0, 5),
                'temperature': temp + np.random.normal(0, 2),
                'light': light + np.random.normal(0, 50),
                'timestamp': None
            }
            for _ in range(5)
        ]
        
        # Calculate trends
        moisture_trend = np.random.normal(0, 3)  # Can be positive or negative
        temp_stability = np.random.uniform(1, 10)
        light_consistency = np.random.uniform(20, 150)
        
        # Calculate health score based on conditions
        score = 50.0  # Base score
        
        # Moisture scoring
        if 40 <= moisture <= 70:
            score += 20
        elif 30 <= moisture < 40 or 70 < moisture <= 80:
            score += 10
        elif moisture < 20 or moisture > 90:
            score -= 20
        
        # Temperature scoring
        if 65 <= temp <= 80:
            score += 15
        elif 60 <= temp < 65 or 80 < temp <= 85:
            score += 8
        elif temp < 55 or temp > 90:
            score -= 15
        
        # Light scoring
        if 300 <= light <= 800:
            score += 15
        elif 200 <= light < 300 or 800 < light <= 1000:
            score += 8
        elif light < 100 or light > 1500:
            score -= 15
        
        # Trend penalty
        if moisture_trend < -5:
            score -= 10
        elif moisture_trend > 2:
            score += 5
        
        # Weather stress
        if weather_temp > 80 and weather_humidity < 40:
            score -= 5
        elif weather_temp < 65 and weather_humidity > 75:
            score -= 3
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Extract features using the model's method
        weather_data = {
            'temperature': weather_temp,
            'humidity': weather_humidity,
            'precipitation': weather_precip
        }
        
        # Generate plant data with defaults (simulating what we'll have when plant data is available)
        plant_data = {
            'age_days': np.random.randint(1, 365),
            'plant_type': np.random.choice(['succulent', 'herb', 'vegetable', 'flower', 'tree']),
            'optimal_moisture_min': np.random.uniform(30, 50),
            'optimal_moisture_max': np.random.uniform(50, 80),
            'optimal_temp_min': np.random.uniform(60, 70),
            'optimal_temp_max': np.random.uniform(75, 85),
            'optimal_light_min': np.random.uniform(200, 400),
            'optimal_light_max': np.random.uniform(600, 1000),
            'watering_frequency_days': np.random.uniform(1, 7),
            'days_since_last_watering': np.random.uniform(0, 7),
            'care_level': np.random.choice(['low', 'medium', 'high']),
            'native_climate': np.random.choice(['arid', 'temperate', 'tropical', 'subtropical'])
        }
        
        classifier = PlantHealthClassifier()
        features = classifier.extract_features(sensor_readings, weather_data, plant_data)
        
        X.append(features)
        y.append(score)
    
    return np.array(X), np.array(y)


if __name__ == '__main__':
    print("Generating synthetic health training data...")
    X, y = generate_synthetic_health_data(n_samples=500)
    
    print(f"Generated {len(X)} samples")
    print(f"Score distribution:")
    print(f"  Critical (0-29): {np.sum((y >= 0) & (y <= 29))}")
    print(f"  Poor (30-49): {np.sum((y >= 30) & (y <= 49))}")
    print(f"  Fair (50-64): {np.sum((y >= 50) & (y <= 64))}")
    print(f"  Good (65-79): {np.sum((y >= 65) & (y <= 79))}")
    print(f"  Excellent (80-100): {np.sum((y >= 80) & (y <= 100))}")
    
    print("\nTraining health classifier...")
    classifier = PlantHealthClassifier()
    metrics = classifier.train(X, y, verbose=True)
    
    print("\nTesting predictions...")
    test_cases = [
        {
            'sensor_readings': [
                {'moisture': 45, 'temperature': 72, 'light': 500, 'timestamp': None},
                {'moisture': 47, 'temperature': 71, 'light': 480, 'timestamp': None},
                {'moisture': 50, 'temperature': 73, 'light': 520, 'timestamp': None},
            ],
            'weather_data': {'temperature': 75, 'humidity': 60, 'precipitation': 0}
        },
        {
            'sensor_readings': [
                {'moisture': 15, 'temperature': 85, 'light': 200, 'timestamp': None},
                {'moisture': 18, 'temperature': 87, 'light': 180, 'timestamp': None},
                {'moisture': 20, 'temperature': 86, 'light': 220, 'timestamp': None},
            ],
            'weather_data': {'temperature': 88, 'humidity': 30, 'precipitation': 0}
        },
        {
            'sensor_readings': [
                {'moisture': 60, 'temperature': 68, 'light': 600, 'timestamp': None},
                {'moisture': 58, 'temperature': 69, 'light': 580, 'timestamp': None},
                {'moisture': 62, 'temperature': 70, 'light': 620, 'timestamp': None},
            ],
            'weather_data': {'temperature': 70, 'humidity': 65, 'precipitation': 10}
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        result = classifier.predict(test_case)
        print(f"\nTest Case {i}:")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Score Estimate: {result['score_estimate']:.1f}/100")
        print(f"  Probabilities:")
        for cat, prob in sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {cat}: {prob:.2%}")
    
    # Show feature importance
    importance = classifier.get_feature_importance()
    if importance:
        print("\nFeature Importance:")
        for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"  {feature}: {score:.3f}")

