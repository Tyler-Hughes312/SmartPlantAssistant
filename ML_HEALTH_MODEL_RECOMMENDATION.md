# ML Model Recommendation: Plant Health Prediction

## Problem Analysis

**Goal**: Predict plant health using:
- Historical weather data (temperature, humidity, precipitation trends)
- Current weather data
- Historical sensor data (moisture, light, temperature trends)
- Current sensor readings

**Output Options**:
1. **Regression**: Predict score (0-100)
2. **Classification**: Predict category (Excellent/Good/Fair/Poor/Critical)

---

## Recommendation: **Multi-Class Classification** ✅

### Why Classification Over Regression?

1. **More Interpretable**
   - "Your plant is in Poor health" is clearer than "Score: 42.3"
   - Users understand categories better than numeric scores

2. **Actionable**
   - Each category can map to specific actions:
     - Critical → Water immediately, check for disease
     - Poor → Adjust watering schedule, check light
     - Fair → Monitor closely
     - Good → Minor adjustments needed
     - Excellent → All good, keep doing what you're doing

3. **Better for Decision Making**
   - Categories provide clear thresholds for intervention
   - Easier to set up alerts/notifications

4. **Handles Imbalanced Data Better**
   - Most plants are probably "Good" or "Fair"
   - Classification can handle this imbalance better than regression

5. **Can Still Show Confidence**
   - "Excellent (85% confidence)" or "Good (60% confidence, might be Fair)"
   - Provides nuance while keeping simplicity

### Recommended Categories

**5-Class Classification**:
1. **Excellent** (80-100): All conditions optimal, thriving
2. **Good** (65-79): Minor improvements possible, healthy
3. **Fair** (50-64): Some conditions need attention
4. **Poor** (30-49): Multiple factors need immediate attention
5. **Critical** (0-29): Plant in distress, urgent action needed

**Alternative: 3-Class** (Simpler):
1. **Healthy**: Score 65-100
2. **Needs Attention**: Score 30-64
3. **Critical**: Score 0-29

---

## Model Architecture: **Random Forest Classifier**

### Why Random Forest?

1. **Handles Mixed Data Types**
   - Can work with continuous (temperature, humidity) and categorical data
   - Handles missing values well

2. **Feature Importance**
   - Shows which factors matter most (moisture trends? weather? light?)

3. **Robust to Overfitting**
   - Works well with limited data
   - Good generalization

4. **Interpretable**
   - Can see which features drive each prediction
   - Can explain why plant is "Poor" vs "Good"

### Alternative: **Gradient Boosting (XGBoost)**
- Better accuracy if you have lots of data (500+ samples)
- More complex, harder to interpret

---

## Feature Engineering

### Current Features (from existing health score):
- Current moisture, temperature, light
- Recent trends (moisture decline, temperature stability)

### Additional Features for ML Model:

**Historical Trends** (last 7 days):
1. **Moisture Trend**: Average change rate, volatility
2. **Temperature Trend**: Average, min, max, volatility
3. **Light Trend**: Average, consistency
4. **Weather Trends**: 
   - Average temperature
   - Average humidity
   - Total precipitation
   - Temperature volatility
   - Humidity volatility

**Current Conditions**:
5. Current moisture, temperature, light
6. Current weather (temp, humidity, precipitation)

**Derived Features**:
7. **Days since last watering** (if tracked)
8. **Moisture deviation from optimal** (|moisture - 50|)
9. **Temperature deviation from optimal** (|temp - 72.5|)
10. **Light deviation from optimal** (|light - 550|)
11. **Weather stress index**: High temp + low humidity = stress

**Time-based Features**:
12. **Day of week** (watering patterns)
13. **Hours since sunrise** (affects light)
14. **Season** (if available)

---

## Training Data Requirements

### Minimum:
- **100 samples**: Basic model
- **300 samples**: Good performance
- **500+ samples**: Excellent performance

### Data Collection Strategy:

1. **Use Existing Health Scores**
   - Extract features from historical sensor readings
   - Use current health score calculation as ground truth
   - Convert scores to categories:
     - 80-100 → Excellent
     - 65-79 → Good
     - 50-64 → Fair
     - 30-49 → Poor
     - 0-29 → Critical

2. **Synthetic Data** (for initial training)
   - Generate realistic scenarios based on domain knowledge
   - Example: Low moisture + declining trend + hot weather → Poor/Critical

3. **Active Learning**
   - As users mark plants as "healthy" or "unhealthy"
   - Use feedback to improve model

---

## Model Evaluation Metrics

### For Classification:
1. **Accuracy**: Overall % correct
2. **Precision/Recall per class**: How well each category is predicted
3. **F1-Score**: Balance of precision and recall
4. **Confusion Matrix**: See which categories get confused

### Business Metrics:
- **False Negatives**: Predicted "Good" but actually "Critical" (BAD!)
- **False Positives**: Predicted "Critical" but actually "Good" (annoying but safer)

---

## Implementation Plan

### Phase 1: Data Collection & Feature Engineering
1. Extract historical sensor readings (last 7 days per plant)
2. Extract historical weather data (if available, or use current)
3. Calculate trends (moisture change rate, temperature stability, etc.)
4. Create feature matrix

### Phase 2: Label Generation
1. Use existing health score calculation
2. Convert scores to categories
3. Create training dataset

### Phase 3: Model Development
1. Split data: 70% train, 15% validation, 15% test
2. Train Random Forest Classifier
3. Tune hyperparameters
4. Evaluate on test set

### Phase 4: Integration
1. Replace current rule-based health score with ML model
2. Add confidence scores
3. Show feature importance (why plant is in this category)

---

## Example Output

**Current (Rule-based)**:
```json
{
  "score": 72,
  "status": "Good"
}
```

**ML Model (Classification)**:
```json
{
  "category": "Good",
  "confidence": 0.85,
  "probabilities": {
    "Excellent": 0.15,
    "Good": 0.85,
    "Fair": 0.00,
    "Poor": 0.00,
    "Critical": 0.00
  },
  "key_factors": [
    "Moisture level is optimal (52%)",
    "Temperature stable (72°F)",
    "Light levels adequate (450 lux)"
  ],
  "recommendations": [
    "Continue current care routine",
    "Monitor moisture trend"
  ]
}
```

---

## Comparison Table

| Aspect | Regression (Score) | Classification (Category) |
|--------|-------------------|---------------------------|
| **Interpretability** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Actionability** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Granularity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **User Understanding** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Alert Thresholds** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Model Complexity** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Data Needs** | Similar | Similar |

---

## Final Recommendation

**Use Multi-Class Classification with Random Forest Classifier**

**Categories**: Excellent, Good, Fair, Poor, Critical (5 classes)

**Why**:
- ✅ More interpretable and actionable
- ✅ Better user experience
- ✅ Can still show confidence/probabilities
- ✅ Easier to set up alerts
- ✅ Better for decision-making

**Implementation**:
- Start with 5 classes (can simplify to 3 later if needed)
- Use Random Forest (can upgrade to XGBoost later)
- Include historical trends as features
- Show confidence and key factors

Would you like me to implement this?

