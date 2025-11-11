"""
Random Forest Classifier Model for Plant Health Classification

This module implements a Random Forest Classifier to predict plant health categories
based on sensor readings, weather data, and historical trends.
"""

import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class PlantHealthClassifier:
    """
    Multi-class classifier for plant health categories.
    
    Categories:
    - Excellent (80-100): All conditions optimal, thriving
    - Good (65-79): Minor improvements possible, healthy
    - Fair (50-64): Some conditions need attention
    - Poor (30-49): Multiple factors need immediate attention
    - Critical (0-29): Plant in distress, urgent action needed
    
    Features:
    - Current sensor readings (moisture, temperature, light)
    - Current weather (temperature, humidity, precipitation)
    - Historical trends (moisture change, temperature stability, light consistency)
    - Derived features (deviations from optimal, stress indices)
    """
    
    CATEGORIES = ['Critical', 'Poor', 'Fair', 'Good', 'Excellent']
    CATEGORY_THRESHOLDS = {
        'Critical': (0, 29),
        'Poor': (30, 49),
        'Fair': (50, 64),
        'Good': (65, 79),
        'Excellent': (80, 100)
    }
    
    def __init__(self, model_path=None):
        """
        Initialize the classifier.
        
        Args:
            model_path: Path to saved model file. If None, creates new model.
        """
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 'health_model.pkl'
        )
        self.is_trained = False
        
        # Load existing model if available
        if os.path.exists(self.model_path):
            try:
                self.load_model()
                print(f"Loaded existing health model from {self.model_path}")
            except Exception as e:
                print(f"Could not load health model: {e}. Creating new model.")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Create a new Random Forest Classifier with recommended hyperparameters."""
        self.model = RandomForestClassifier(
            n_estimators=100,      # Number of trees
            max_depth=15,          # Max depth of trees
            min_samples_split=5,    # Minimum samples to split
            min_samples_leaf=2,     # Minimum samples in leaf
            random_state=42,        # For reproducibility
            n_jobs=-1,              # Use all CPU cores
            class_weight='balanced' # Handle class imbalance
        )
        self.is_trained = False
    
    def extract_features(self, sensor_readings, weather_data, plant_data=None, historical_data=None):
        """
        Extract features from sensor, weather, and plant data.
        
        Args:
            sensor_readings: List of recent sensor readings (most recent first)
                           Each reading: {'moisture': float, 'temperature': float, 'light': float, 'timestamp': datetime}
            weather_data: Current weather dict {'temperature': float, 'humidity': float, 'precipitation': float}
            plant_data: Optional plant-specific data dict:
                       {
                           'plant_type': str,           # e.g., 'succulent', 'herb', 'vegetable'
                           'age_days': int,             # Days since planted
                           'optimal_moisture_min': float,  # Optimal moisture range
                           'optimal_moisture_max': float,
                           'optimal_temp_min': float,     # Optimal temperature range
                           'optimal_temp_max': float,
                           'optimal_light_min': float,    # Optimal light range
                           'optimal_light_max': float,
                           'watering_frequency_days': float,  # Typical watering frequency
                           'days_since_last_watering': float, # Days since last watering
                           'care_level': str,            # 'low', 'medium', 'high'
                           'native_climate': str         # 'tropical', 'temperate', 'arid', etc.
                       }
            historical_data: Optional historical data for trend calculation
        
        Returns:
            np.array: Feature vector (1D array of features)
        """
        features = []
        
        if not sensor_readings or len(sensor_readings) == 0:
            # No sensor data - use defaults
            current_moisture = 50.0
            current_temp = 72.0
            current_light = 500.0
            moisture_trend = 0.0
            temp_stability = 5.0
            light_consistency = 100.0
        else:
            latest = sensor_readings[0]
            current_moisture = latest.get('moisture', 50.0)
            current_temp = latest.get('temperature', 72.0)
            current_light = latest.get('light', 500.0)
            
            # Calculate trends if we have multiple readings
            if len(sensor_readings) >= 3:
                # Moisture trend (change rate)
                moisture_changes = []
                temp_values = []
                light_values = []
                
                for i in range(min(5, len(sensor_readings) - 1)):
                    prev = sensor_readings[i + 1]
                    curr = sensor_readings[i]
                    moisture_changes.append(curr.get('moisture', 50) - prev.get('moisture', 50))
                    temp_values.append(curr.get('temperature', 72))
                    light_values.append(curr.get('light', 500))
                
                moisture_trend = np.mean(moisture_changes) if moisture_changes else 0.0
                temp_stability = np.std(temp_values) if temp_values else 5.0
                light_consistency = np.std(light_values) if light_values else 100.0
            else:
                moisture_trend = 0.0
                temp_stability = 5.0
                light_consistency = 100.0
        
        # Current sensor values
        features.append(current_moisture)
        features.append(current_temp)
        features.append(current_light)
        
        # Current weather values
        weather_temp = weather_data.get('temperature', 72.0) if weather_data else 72.0
        weather_humidity = weather_data.get('humidity', 60.0) if weather_data else 60.0
        weather_precip = weather_data.get('precipitation', 0.0) if weather_data else 0.0
        
        features.append(weather_temp)
        features.append(weather_humidity)
        features.append(weather_precip)
        
        # Trends
        features.append(moisture_trend)
        features.append(temp_stability)
        features.append(light_consistency)
        
        # Derived features
        # Moisture deviation from optimal (50% default, or plant-specific optimal)
        optimal_moisture_center = 50.0
        if plant_data and plant_data.get('optimal_moisture_min') is not None and plant_data.get('optimal_moisture_max') is not None:
            optimal_moisture_center = (plant_data['optimal_moisture_min'] + plant_data['optimal_moisture_max']) / 2
        moisture_dev = abs(current_moisture - optimal_moisture_center)
        features.append(moisture_dev)
        
        # Temperature deviation from optimal (72.5°F default, or plant-specific optimal)
        optimal_temp_center = 72.5
        if plant_data and plant_data.get('optimal_temp_min') is not None and plant_data.get('optimal_temp_max') is not None:
            optimal_temp_center = (plant_data['optimal_temp_min'] + plant_data['optimal_temp_max']) / 2
        temp_dev = abs(current_temp - optimal_temp_center)
        features.append(temp_dev)
        
        # Light deviation from optimal (550 lux default, or plant-specific optimal)
        optimal_light_center = 550.0
        if plant_data and plant_data.get('optimal_light_min') is not None and plant_data.get('optimal_light_max') is not None:
            optimal_light_center = (plant_data['optimal_light_min'] + plant_data['optimal_light_max']) / 2
        light_dev = abs(current_light - optimal_light_center)
        features.append(light_dev)
        
        # Weather stress index (high temp + low humidity = stress)
        # Normalized: 0 (no stress) to 1 (high stress)
        temp_stress = max(0, (weather_temp - 70) / 20) if weather_temp > 70 else 0
        humidity_stress = max(0, (40 - weather_humidity) / 40) if weather_humidity < 40 else 0
        weather_stress = (temp_stress + humidity_stress) / 2
        features.append(min(1.0, weather_stress))
        
        # Moisture status (categorical encoding)
        if current_moisture < 30:
            moisture_status = 0  # Very dry
        elif current_moisture < 50:
            moisture_status = 1  # Dry
        elif current_moisture < 70:
            moisture_status = 2  # Optimal
        else:
            moisture_status = 3  # Wet
        
        features.append(moisture_status)
        
        # Plant-based features (use defaults if not available)
        # Age in days (normalized: 0-365 days -> 0-1)
        age_days = plant_data.get('age_days', 30) if plant_data else 30
        age_normalized = min(1.0, age_days / 365.0)
        features.append(age_normalized)
        
        # Days since last watering (normalized: 0-14 days -> 0-1)
        days_since_watering = plant_data.get('days_since_last_watering', 3.0) if plant_data else 3.0
        days_since_watering_normalized = min(1.0, days_since_watering / 14.0)
        features.append(days_since_watering_normalized)
        
        # Watering frequency (normalized: 1-7 days -> 0-1)
        watering_frequency = plant_data.get('watering_frequency_days', 3.0) if plant_data else 3.0
        watering_frequency_normalized = (watering_frequency - 1.0) / 6.0  # 1-7 days -> 0-1
        features.append(watering_frequency_normalized)
        
        # Care level encoding (low=0, medium=0.5, high=1)
        care_level_map = {'low': 0.0, 'medium': 0.5, 'high': 1.0}
        care_level = care_level_map.get(plant_data.get('care_level', 'medium') if plant_data else 'medium', 0.5)
        features.append(care_level)
        
        # Native climate encoding (arid=0, temperate=0.5, tropical=1)
        climate_map = {'arid': 0.0, 'temperate': 0.5, 'tropical': 1.0, 'subtropical': 0.75}
        native_climate = climate_map.get(plant_data.get('native_climate', 'temperate') if plant_data else 'temperate', 0.5)
        features.append(native_climate)
        
        # Plant type encoding (succulent=0, herb=0.33, vegetable=0.66, other=1)
        plant_type_map = {'succulent': 0.0, 'cactus': 0.0, 'herb': 0.33, 'vegetable': 0.66, 'flower': 0.5, 'tree': 0.83}
        plant_type = plant_type_map.get(plant_data.get('plant_type', 'herb') if plant_data else 'herb', 0.5)
        features.append(plant_type)
        
        # Optimal range compliance (how well current conditions match plant's optimal ranges)
        # 1.0 = perfect match, 0.0 = far from optimal
        moisture_in_range = 1.0
        if plant_data and plant_data.get('optimal_moisture_min') is not None and plant_data.get('optimal_moisture_max') is not None:
            if plant_data['optimal_moisture_min'] <= current_moisture <= plant_data['optimal_moisture_max']:
                moisture_in_range = 1.0
            else:
                # Penalty based on distance from range
                if current_moisture < plant_data['optimal_moisture_min']:
                    distance = plant_data['optimal_moisture_min'] - current_moisture
                else:
                    distance = current_moisture - plant_data['optimal_moisture_max']
                range_size = plant_data['optimal_moisture_max'] - plant_data['optimal_moisture_min']
                moisture_in_range = max(0.0, 1.0 - (distance / range_size))
        
        temp_in_range = 1.0
        if plant_data and plant_data.get('optimal_temp_min') is not None and plant_data.get('optimal_temp_max') is not None:
            if plant_data['optimal_temp_min'] <= current_temp <= plant_data['optimal_temp_max']:
                temp_in_range = 1.0
            else:
                if current_temp < plant_data['optimal_temp_min']:
                    distance = plant_data['optimal_temp_min'] - current_temp
                else:
                    distance = current_temp - plant_data['optimal_temp_max']
                range_size = plant_data['optimal_temp_max'] - plant_data['optimal_temp_min']
                temp_in_range = max(0.0, 1.0 - (distance / range_size))
        
        light_in_range = 1.0
        if plant_data and plant_data.get('optimal_light_min') is not None and plant_data.get('optimal_light_max') is not None:
            if plant_data['optimal_light_min'] <= current_light <= plant_data['optimal_light_max']:
                light_in_range = 1.0
            else:
                if current_light < plant_data['optimal_light_min']:
                    distance = plant_data['optimal_light_min'] - current_light
                else:
                    distance = current_light - plant_data['optimal_light_max']
                range_size = plant_data['optimal_light_max'] - plant_data['optimal_light_min']
                light_in_range = max(0.0, 1.0 - (distance / range_size))
        
        # Average compliance score
        optimal_compliance = (moisture_in_range + temp_in_range + light_in_range) / 3.0
        features.append(optimal_compliance)
        
        return np.array(features)
    
    def score_to_category(self, score):
        """Convert numeric score (0-100) to category."""
        for category, (min_score, max_score) in self.CATEGORY_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return category
        return 'Fair'  # Default
    
    def train(self, X, y, test_size=0.2, verbose=True):
        """
        Train the classifier on provided data.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,) - category labels or scores (0-100)
            test_size: Fraction of data to use for testing
            verbose: Print training metrics
        
        Returns:
            dict: Training metrics (accuracy, classification report)
        """
        if len(X) < 20:
            raise ValueError("Need at least 20 samples to train the model")
        
        # Convert scores to categories if needed
        y_categories = []
        for label in y:
            if isinstance(label, (int, float)) and 0 <= label <= 100:
                y_categories.append(self.score_to_category(label))
            else:
                y_categories.append(str(label))
        
        y_categories = np.array(y_categories)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_categories, test_size=test_size, random_state=42, stratify=y_categories
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        metrics = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'n_samples': len(X),
            'n_train': len(X_train),
            'n_test': len(X_test),
            'classification_report': classification_report(y_test, test_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, test_pred).tolist()
        }
        
        if verbose:
            print("\n" + "="*60)
            print("HEALTH MODEL TRAINING RESULTS")
            print("="*60)
            print(f"Training samples: {len(X_train)}")
            print(f"Test samples: {len(X_test)}")
            print(f"\nTraining Accuracy: {train_acc:.3f}")
            print(f"Test Accuracy: {test_acc:.3f}")
            print("\nClassification Report:")
            print(classification_report(y_test, test_pred))
            print("="*60 + "\n")
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict(self, features):
        """
        Predict plant health category.
        
        Args:
            features: Feature vector (1D array of 15 features) or dict with sensor/weather data
        
        Returns:
            dict: {
                'category': str,           # Predicted category
                'confidence': float,       # Confidence score (0-1)
                'probabilities': dict,      # Probability for each category
                'score_estimate': float     # Estimated numeric score (0-100)
            }
        """
        # If features is a dict, extract features
        if isinstance(features, dict):
            sensor_readings = features.get('sensor_readings', [])
            weather_data = features.get('weather_data', {})
            plant_data = features.get('plant_data')
            historical_data = features.get('historical_data')
            features = self.extract_features(sensor_readings, weather_data, plant_data, historical_data)
        
        # Ensure features is 2D array
        if isinstance(features, list):
            features = np.array(features)
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        if not self.is_trained:
            # Fallback to rule-based prediction
            return self._rule_based_predict(features[0])
        
        # Predict category
        category = self.model.predict(features)[0]
        
        # Get probabilities
        probabilities = self.model.predict_proba(features)[0]
        prob_dict = dict(zip(self.model.classes_, probabilities))
        
        # Confidence is the probability of the predicted category
        confidence = prob_dict.get(category, 0.5)
        
        # Estimate numeric score from category
        min_score, max_score = self.CATEGORY_THRESHOLDS[category]
        score_estimate = (min_score + max_score) / 2
        
        return {
            'category': category,
            'confidence': float(confidence),
            'probabilities': prob_dict,
            'score_estimate': float(score_estimate)
        }
    
    def _rule_based_predict(self, features):
        """Fallback rule-based prediction when model is not trained."""
        # Extract key features (handle variable feature count)
        moisture = features[0] if len(features) > 0 else 50.0
        temp = features[1] if len(features) > 1 else 72.0
        light = features[2] if len(features) > 2 else 500.0
        moisture_trend = features[6] if len(features) > 6 else 0.0
        # Plant-based features (if available)
        optimal_compliance = features[21] if len(features) > 21 else 0.7  # Default moderate compliance
        
        # Simple rule-based scoring
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
        
        # Optimal compliance bonus/penalty (if plant data available)
        if len(features) > 21:
            optimal_compliance = features[21]
            # Adjust score based on how well conditions match plant's optimal ranges
            score += (optimal_compliance - 0.7) * 20  # Bonus if >70% compliant, penalty if <70%
        
        score = max(0, min(100, score))
        category = self.score_to_category(score)
        
        return {
            'category': category,
            'confidence': 0.65,  # Lower confidence for rule-based
            'probabilities': {category: 1.0},
            'score_estimate': score
        }
    
    def get_feature_importance(self):
        """
        Get feature importance scores.
        
        Returns:
            dict: Feature names and their importance scores
        """
        if not self.is_trained:
            return None
        
        feature_names = [
            # Sensor readings (3)
            'moisture', 'temperature', 'light',
            # Weather data (3)
            'weather_temp', 'weather_humidity', 'weather_precip',
            # Trends (3)
            'moisture_trend', 'temp_stability', 'light_consistency',
            # Deviations from optimal (3)
            'moisture_deviation', 'temp_deviation', 'light_deviation',
            # Weather stress (1)
            'weather_stress',
            # Moisture status (1)
            'moisture_status',
            # Plant-based features (8)
            'age_days_normalized',
            'days_since_watering_normalized',
            'watering_frequency_normalized',
            'care_level',
            'native_climate',
            'plant_type',
            'optimal_compliance'
        ]
        
        importances = self.model.feature_importances_
        return dict(zip(feature_names, importances))
    
    def save_model(self):
        """Save the trained model to disk."""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'is_trained': self.is_trained,
                    'categories': self.CATEGORIES
                }, f)
            print(f"Health model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving health model: {e}")
    
    def load_model(self):
        """Load a trained model from disk."""
        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.is_trained = data.get('is_trained', True)
            if 'categories' in data:
                self.CATEGORIES = data['categories']
        print(f"Health model loaded from {self.model_path}")

