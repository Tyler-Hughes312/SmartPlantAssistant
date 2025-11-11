# Weather-Only Prediction Model

Since you only have weather data (temperature, humidity, precipitation) and no moisture sensor data,
we need to create a model that predicts watering needs based on weather conditions alone.

## Approach: Weather-Based Evapotranspiration Model

Instead of predicting "hours until watering" (which requires moisture data),
we can predict "evapotranspiration rate" - how fast water is being lost from the soil.

This tells us:
- High evapotranspiration = water more frequently
- Low evapotranspiration = water less frequently

## Features Available:
- Temperature (°F)
- Humidity (%)
- Precipitation probability (%)

## Model Output:
- Evapotranspiration rate (mm/day or relative scale)
- Days until watering needed (estimated based on typical soil moisture)

## Alternative: Rule-Based Weather Model

Since we can't train without moisture data, we can use:
1. **Evapotranspiration formula** (scientific, based on weather)
2. **Weather patterns** (hot + dry = water more often)

This doesn't require training data - it's based on agricultural science.

