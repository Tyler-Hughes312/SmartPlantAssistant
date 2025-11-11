"""
Random Forest Regressor Model for Plant Watering Prediction

This module implements a Random Forest model to predict hours until watering
based on sensor and weather data.
"""

import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class WateringPredictionModel:
    """
    Weather-based model for predicting watering needs.
    
    Since moisture sensor data is not available, this model uses:
    - temperature: Temperature in Fahrenheit
    - humidity: Humidity percentage (0-100)
    - precipitation: Precipitation probability (0-100)
    
    The model predicts watering needs based on evapotranspiration rates
    calculated from weather conditions.
    
    Output:
    - hours_until_watering: Estimated hours until watering needed (6-168 hours)
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the model.
        
        Args:
            model_path: Path to saved model file. If None, creates new model.
        """
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), 'watering_model.pkl'
        )
        self.is_trained = False
        
        # Load existing model if available
        if os.path.exists(self.model_path):
            try:
                self.load_model()
                print(f"Loaded existing model from {self.model_path}")
            except Exception as e:
                print(f"Could not load model: {e}. Creating new model.")
                self._create_new_model()
        else:
            self._create_new_model()
    
    def _create_new_model(self):
        """Create a new Random Forest model with recommended hyperparameters."""
        self.model = RandomForestRegressor(
            n_estimators=100,      # Number of trees
            max_depth=10,          # Max depth of trees
            min_samples_split=5,    # Minimum samples to split
            min_samples_leaf=2,     # Minimum samples in leaf
            random_state=42,        # For reproducibility
            n_jobs=-1              # Use all CPU cores
        )
        self.is_trained = False
    
    def train(self, X, y, test_size=0.2, verbose=True):
        """
        Train the model on provided data.
        
        Args:
            X: Feature matrix (n_samples, n_features)
               Features: [moisture, temperature, humidity, precipitation]
            y: Target vector (n_samples,) - hours until watering
            test_size: Fraction of data to use for testing
            verbose: Print training metrics
        
        Returns:
            dict: Training metrics (MAE, RMSE, R²)
        """
        if len(X) < 10:
            raise ValueError("Need at least 10 samples to train the model")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        metrics = {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'n_samples': len(X),
            'n_train': len(X_train),
            'n_test': len(X_test)
        }
        
        if verbose:
            print("\n" + "="*60)
            print("MODEL TRAINING RESULTS")
            print("="*60)
            print(f"Training samples: {len(X_train)}")
            print(f"Test samples: {len(X_test)}")
            print(f"\nTraining Metrics:")
            print(f"  MAE:  {train_mae:.2f} hours")
            print(f"  RMSE: {train_rmse:.2f} hours")
            print(f"  R²:   {train_r2:.3f}")
            print(f"\nTest Metrics:")
            print(f"  MAE:  {test_mae:.2f} hours")
            print(f"  RMSE: {test_rmse:.2f} hours")
            print(f"  R²:   {test_r2:.3f}")
            print("="*60 + "\n")
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict(self, features):
        """
        Predict hours until watering based on weather conditions.
        
        Args:
            features: List or array of features [temperature, humidity, precipitation]
                     OR [moisture, temperature, humidity, precipitation] if moisture available
        
        Returns:
            float: Hours until watering (clamped between 6-168 hours)
        """
        # Handle different feature formats
        if len(features) == 4:
            # Has moisture data: [moisture, temperature, humidity, precipitation]
            moisture, temperature, humidity, precipitation = features
            use_moisture = True
        elif len(features) == 3:
            # Weather only: [temperature, humidity, precipitation]
            temperature, humidity, precipitation = features
            moisture = None
            use_moisture = False
        else:
            raise ValueError(f"Expected 3 or 4 features, got {len(features)}")
        
        if not self.is_trained:
            # Use weather-based evapotranspiration prediction
            result = self._weather_based_predict(temperature, humidity, precipitation, moisture)
            # Return frequency_days if no moisture, hours_until if moisture available
            if moisture is None:
                return result.get('frequency_days')
            else:
                return result.get('hours_until')
        
        # If model is trained and we have moisture, use it
        if use_moisture:
            # Check if model expects 4 features (moisture + weather) or 3 (weather only)
            if self.is_trained and hasattr(self.model, 'n_features_in_'):
                expected_features = self.model.n_features_in_
                if expected_features == 3:
                    # Model was trained with weather-only (3 features)
                    # Use weather-based prediction instead
                    result = self._weather_based_predict(temperature, humidity, precipitation, moisture)
                    return result.get('hours_until')
                elif expected_features == 4:
                    # Model expects 4 features - use it
                    # Ensure features is 2D array
                    if isinstance(features, list):
                        features = np.array(features).reshape(1, -1)
                    elif features.ndim == 1:
                        features = features.reshape(1, -1)
                    
                    # Predict hours until watering
                    hours = self.model.predict(features)[0]
                    
                    # Clamp between 6 and 168 hours (1 week max)
                    hours = max(6, min(168, hours))
                    
                    return float(hours)
                else:
                    # Unexpected feature count - use weather-based
                    result = self._weather_based_predict(temperature, humidity, precipitation, moisture)
                    return result.get('hours_until')
            else:
                # Model not trained or doesn't have feature info - use weather-based
                result = self._weather_based_predict(temperature, humidity, precipitation, moisture)
                return result.get('hours_until')
        else:
            # No moisture - check if model expects 3 features
            if self.is_trained and hasattr(self.model, 'n_features_in_'):
                expected_features = self.model.n_features_in_
                if expected_features == 3:
                    # Model expects 3 features - use it
                    # Ensure features is 2D array
                    if isinstance(features, list):
                        features = np.array(features).reshape(1, -1)
                    elif features.ndim == 1:
                        features = features.reshape(1, -1)
                    
                    # Predict frequency
                    frequency = self.model.predict(features)[0]
                    # Clamp between 1 and 7 days
                    frequency = max(1.0, min(7.0, frequency))
                    return float(frequency)
                else:
                    # Model expects different features - use weather-based
                    result = self._weather_based_predict(temperature, humidity, precipitation, None)
                    return result.get('frequency_days')
            else:
                # Model not trained - use weather-based frequency
                result = self._weather_based_predict(temperature, humidity, precipitation, None)
                return result.get('frequency_days')
    
    def _weather_based_predict(self, temperature, humidity, precipitation, moisture=None):
        """
        Predict watering frequency based on weather conditions using evapotranspiration.
        
        When moisture data is NOT available, this returns watering frequency (days).
        When moisture data IS available, returns hours until next watering.
        
        Args:
            temperature: Temperature in Fahrenheit
            humidity: Humidity percentage (0-100)
            precipitation: Precipitation probability (0-100)
            moisture: Optional moisture value if available
        
        Returns:
            dict: {
                'frequency_days': float,  # Days between watering (when no moisture)
                'hours_until': float      # Hours until watering (when moisture available)
            }
        """
        # Simplified evapotranspiration calculation
        # Higher temperature = more evaporation
        # Lower humidity = more evaporation
        
        # Temperature factor (normalized 0-1, higher temp = higher factor)
        temp_factor = (temperature - 60) / 30  # 60°F = 0, 90°F = 1
        temp_factor = max(0, min(1, temp_factor))
        
        # Humidity factor (normalized 0-1, lower humidity = higher factor)
        humidity_factor = (100 - humidity) / 70  # 100% = 0, 30% = 1
        humidity_factor = max(0, min(1, humidity_factor))
        
        # Combined ET rate (0-1 scale)
        # Weight temperature more heavily (60% temp, 40% humidity)
        et_rate = 0.6 * temp_factor + 0.4 * humidity_factor
        
        # Calculate watering frequency (days between watering)
        # High ET (hot, dry) = water more frequently (fewer days)
        # Low ET (cool, humid) = water less frequently (more days)
        # Range: 1 day (very hot/dry) to 5 days (cool/humid)
        base_days = 1.0 + (1.0 - et_rate) * 4.0  # Range: 1-5 days
        
        # Adjust for precipitation
        # High precipitation = less watering needed (more days between)
        precip_adjustment = 1.0 + (precipitation / 100) * 0.5  # Up to 50% increase
        frequency_days = base_days * precip_adjustment
        
        # Clamp frequency between 1 and 7 days
        frequency_days = max(1.0, min(7.0, frequency_days))
        
        # If moisture data is available, calculate hours until watering
        if moisture is not None:
            # Convert frequency to hours as baseline
            base_hours = frequency_days * 24
            
            # Adjust based on current moisture level
            if moisture < 30:
                hours = base_hours * 0.3  # Very dry - water much sooner
            elif moisture < 40:
                hours = base_hours * 0.5  # Dry - water sooner
            elif moisture < 50:
                hours = base_hours * 0.7  # Moderate - slight adjustment
            else:
                hours = base_hours  # Good moisture - use frequency-based prediction
            
            # Clamp between 6 and 168 hours (1 week max)
            hours = max(6, min(168, hours))
            return {'frequency_days': frequency_days, 'hours_until': float(hours)}
        else:
            # No moisture data - return frequency only
            return {'frequency_days': float(frequency_days), 'hours_until': None}
    
    def get_feature_importance(self):
        """
        Get feature importance scores.
        
        Returns:
            dict: Feature names and their importance scores
        """
        if not self.is_trained:
            return None
        
        # Feature names depend on whether moisture is available
        if self.model.n_features_in_ == 4:
            feature_names = ['moisture', 'temperature', 'humidity', 'precipitation']
        else:
            feature_names = ['temperature', 'humidity', 'precipitation']
        importances = self.model.feature_importances_
        
        return dict(zip(feature_names, importances))
    
    def save_model(self):
        """Save the trained model to disk."""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'is_trained': self.is_trained
                }, f)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load a trained model from disk."""
        with open(self.model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.is_trained = data.get('is_trained', True)
        print(f"Model loaded from {self.model_path}")


def generate_synthetic_training_data(n_samples=500, include_moisture=False):
    """
    Generate synthetic training data based on weather conditions.
    
    Since moisture data is not available, this generates training data
    using evapotranspiration calculations from weather.
    
    Args:
        n_samples: Number of training samples to generate
        include_moisture: If True, include moisture as a feature (for when sensors are available)
    
    Returns:
        tuple: (X, y) where X is features and y is target
    """
    np.random.seed(42)
    X = []
    y = []
    
    # Create a temporary model to use its weather-based prediction
    temp_model = WateringPredictionModel()
    temp_model.is_trained = False  # Force use of weather-based prediction
    
    for _ in range(n_samples):
        # Generate realistic weather values
        temperature = np.random.uniform(60, 85)  # 60-85°F
        humidity = np.random.uniform(30, 80)  # 30-80% humidity
        precipitation = np.random.uniform(0, 50)  # 0-50% chance
        
        if include_moisture:
            moisture = np.random.uniform(20, 80)  # 20-80% moisture
            features = [moisture, temperature, humidity, precipitation]
        else:
            features = [temperature, humidity, precipitation]
        
        # Use weather-based prediction to generate target
        hours = temp_model._weather_based_predict(temperature, humidity, precipitation, 
                                                   moisture if include_moisture else None)
        
        # Add some realistic noise
        hours += np.random.normal(0, hours * 0.1)  # 10% noise
        hours = max(6, min(168, hours))  # Clamp to 6-168 hours
        
        X.append(features)
        y.append(hours)
    
    return np.array(X), np.array(y)


if __name__ == '__main__':
    # Example usage
    print("Generating synthetic training data...")
    X, y = generate_synthetic_training_data(n_samples=500)
    
    print("Training model...")
    model = WateringPredictionModel()
    metrics = model.train(X, y)
    
    print("\nTesting predictions...")
    test_cases = [
        [30, 75, 50, 0],   # Low moisture, warm, moderate humidity, no rain
        [60, 70, 60, 20],  # Good moisture, moderate temp, good humidity, some rain
        [25, 80, 40, 0],   # Very dry, hot, low humidity, no rain
    ]
    
    for features in test_cases:
        pred = model.predict(features)
        print(f"Features: {features} -> Predicted: {pred:.1f} hours")
    
    # Show feature importance
    importance = model.get_feature_importance()
    if importance:
        print("\nFeature Importance:")
        for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
            print(f"  {feature}: {score:.3f}")

