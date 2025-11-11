# ML Model Recommendation: Plant Watering Prediction

## Problem Analysis

**Task**: Predict when a plant needs to be watered next (in hours/days)

**Input Features**:
- Current moisture content (sensor data)
- Temperature (sensor + weather data)
- Humidity (weather data)
- Precipitation (weather data)

**Output**: Hours until next watering (continuous value, regression problem)

**Current Model**: Simple single-layer neural network with hardcoded weights (not trained on real data)

---

## Recommended Model: **Random Forest Regressor**

### Why Random Forest?

1. **Handles Non-Linear Relationships**
   - Moisture decay isn't linear (evaporation rates change with conditions)
   - Temperature and humidity interact in complex ways
   - Random Forest captures these interactions automatically

2. **Interpretable**
   - Can see which features are most important
   - Understand why predictions are made
   - Better for debugging and user trust

3. **Robust to Small Datasets**
   - Works well even with limited training data
   - Less prone to overfitting than deep neural networks
   - Good performance with 100+ samples

4. **Handles Feature Interactions**
   - Automatically learns how features combine (e.g., high temp + low humidity = faster drying)
   - No need to manually engineer interaction features

5. **No Feature Scaling Required**
   - Works with raw feature values
   - Less preprocessing needed

### Alternative Models (Ranked)

#### 2. **Gradient Boosting (XGBoost/LightGBM)** ⭐ Best Performance
- **Pros**: Often best accuracy, handles non-linear relationships well
- **Cons**: Less interpretable, requires more tuning, needs more data
- **Best for**: When you have 500+ training samples and want maximum accuracy

#### 3. **Neural Network (Multi-Layer)** ⭐ Most Flexible
- **Pros**: Can capture very complex patterns, good for large datasets
- **Cons**: Needs lots of data (1000+ samples), less interpretable, requires more computation
- **Best for**: When you have extensive historical data and want to capture deep patterns

#### 4. **Linear Regression** ⭐ Simplest
- **Pros**: Very interpretable, fast, simple
- **Cons**: Assumes linear relationships (not realistic for this problem)
- **Best for**: Baseline model or when relationships are truly linear

#### 5. **Support Vector Regression (SVR)** ⭐ Good Alternative
- **Pros**: Handles non-linear relationships with kernels, robust
- **Cons**: Slower training, less interpretable than Random Forest
- **Best for**: When Random Forest doesn't perform well

---

## Recommended Approach: Random Forest Regressor

### Model Architecture

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Features (X):
# - current_moisture (0-100%)
# - temperature (°F)
# - humidity (%)
# - precipitation_probability (%)

# Target (y):
# - hours_until_watering (continuous value)
```

### Key Hyperparameters

```python
RandomForestRegressor(
    n_estimators=100,        # Number of trees (more = better, but slower)
    max_depth=10,            # Max depth of trees (prevents overfitting)
    min_samples_split=5,     # Minimum samples to split a node
    min_samples_leaf=2,      # Minimum samples in a leaf node
    random_state=42          # For reproducibility
)
```

### Why These Settings?

- **n_estimators=100**: Good balance of accuracy and speed
- **max_depth=10**: Prevents overfitting while capturing patterns
- **min_samples_split=5**: Ensures robust splits (good for small datasets)
- **min_samples_leaf=2**: Prevents overfitting to outliers

---

## Feature Engineering Recommendations

### Core Features (Required)
1. **current_moisture**: Current soil moisture percentage (0-100)
2. **temperature**: Current temperature (°F)
3. **humidity**: Current humidity (%)
4. **precipitation**: Precipitation probability (%)

### Additional Features (Recommended)
5. **moisture_trend**: Rate of moisture change over last 24 hours
   - `(moisture_24h_ago - current_moisture) / 24`
6. **evapotranspiration**: Calculated water loss rate
   - `temperature * 0.05 + wind_speed * 0.1 - humidity * 0.02`
7. **moisture_deficit**: How far below optimal moisture
   - `max(0, 50 - current_moisture)`  # Assuming 50% is optimal
8. **time_since_last_watering**: Hours since last watering event
   - Requires tracking watering events in database

### Optional Features (If Available)
9. **plant_type**: Categorical (drought-tolerant vs. water-loving)
10. **pot_size**: Size of container (affects drying rate)
11. **sun_exposure**: Light level (lux)
12. **season**: Month or season (affects evaporation)

---

## Training Data Requirements

### Minimum Data Needed
- **50-100 samples**: Basic model that works
- **200-500 samples**: Good performance
- **1000+ samples**: Excellent performance

### Data Collection Strategy

1. **Historical Data**: Use existing sensor readings
   - Extract features at each timestamp
   - Calculate target: time until next watering event

2. **Synthetic Data**: Generate realistic training examples
   - Use domain knowledge to create scenarios
   - Example: Low moisture + high temp + low humidity = water soon

3. **Active Learning**: Collect data as you use the system
   - Track when plants are actually watered
   - Use predictions vs. actual watering times as training data

### Target Variable (y)

**Hours until watering needed**: 
- Calculate from historical data: time between low moisture reading and next watering event
- Or use threshold: hours until moisture drops below critical level (e.g., 30%)

---

## Model Evaluation Metrics

### Primary Metrics
1. **Mean Absolute Error (MAE)**: Average hours off from actual
   - Good: < 12 hours
   - Excellent: < 6 hours

2. **Root Mean Squared Error (RMSE)**: Penalizes large errors more
   - Good: < 18 hours
   - Excellent: < 10 hours

3. **R² Score**: How well model explains variance
   - Good: > 0.7
   - Excellent: > 0.85

### Business Metrics
- **Accuracy within 24 hours**: % of predictions within 24 hours of actual
- **False positives**: Predicted watering when not needed
- **False negatives**: Missed watering when needed

---

## Implementation Plan

### Phase 1: Data Collection & Preparation
1. Extract historical sensor readings from database
2. Match with weather data (if available)
3. Calculate target variable (hours until watering)
4. Create training dataset

### Phase 2: Model Development
1. Split data: 70% train, 15% validation, 15% test
2. Train Random Forest model
3. Tune hyperparameters using validation set
4. Evaluate on test set

### Phase 3: Integration
1. Replace current hardcoded model
2. Add model persistence (save/load trained model)
3. Add retraining capability (update model with new data)

### Phase 4: Monitoring & Improvement
1. Track prediction accuracy over time
2. Collect user feedback (actual watering times)
3. Retrain model periodically with new data

---

## Comparison Table

| Model | Accuracy | Interpretability | Training Speed | Data Needs | Complexity |
|-------|----------|------------------|----------------|------------|------------|
| **Random Forest** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| XGBoost | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Neural Network | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Linear Regression | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

---

## Final Recommendation

**Start with Random Forest Regressor** because:
1. ✅ Best balance of accuracy and interpretability
2. ✅ Works well with limited data
3. ✅ Easy to implement and debug
4. ✅ Can see feature importance
5. ✅ Good baseline to compare against

**Upgrade to XGBoost later** if:
- You collect 500+ training samples
- Random Forest accuracy isn't sufficient
- You want maximum performance

**Consider Neural Network** if:
- You have 1000+ samples
- You want to capture very complex patterns
- You have computational resources

---

## Next Steps

1. **Collect Training Data**: Extract historical sensor readings
2. **Prepare Features**: Create feature matrix (moisture, temp, humidity, precipitation)
3. **Create Target**: Calculate hours until watering for each sample
4. **Train Model**: Use Random Forest with recommended hyperparameters
5. **Evaluate**: Check MAE, RMSE, R² scores
6. **Deploy**: Replace current model in `backend/app.py`

Would you like me to implement this model?

