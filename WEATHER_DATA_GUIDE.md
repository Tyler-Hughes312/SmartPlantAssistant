# Weather Data Guide - NWS API

## Current Weather Data Structure

Your app currently returns this simplified weather object:

```json
{
  "temperature": 72.5,
  "humidity": 65.0,
  "precipitation": 20,
  "windSpeed": 7.5,
  "forecast": "Partly Cloudy",
  "description": "Partly cloudy with a chance of showers...",
  "timestamp": "2024-01-15T14:30:00"
}
```

## What's Available from NWS API

The National Weather Service API provides **much more data** than what's currently displayed. Here's what you can access:

### 1. Forecast Period Data (`current_period`)

Each forecast period includes:

```json
{
  "number": 1,
  "name": "This Afternoon",
  "startTime": "2024-01-15T12:00:00-05:00",
  "endTime": "2024-01-15T18:00:00-05:00",
  "isDaytime": true,
  "temperature": 72,
  "temperatureUnit": "F",
  "temperatureTrend": null,
  "windSpeed": "5 to 10 mph",
  "windDirection": "SW",
  "icon": "https://api.weather.gov/icons/land/day/skc?size=medium",
  "shortForecast": "Sunny",
  "detailedForecast": "Sunny, with a high near 72...",
  "relativeHumidity": {
    "value": 65,
    "unitCode": "wmoUnit:percent"
  },
  "probabilityOfPrecipitation": {
    "value": 0,
    "unitCode": "wmoUnit:percent"
  },
  "dewpoint": {
    "value": 55.0,
    "unitCode": "wmoUnit:degF"
  },
  "heatIndex": {
    "value": 75.0,
    "unitCode": "wmoUnit:degF"
  },
  "windChill": null
}
```

### 2. Observation Data (Real-time measurements)

From the latest observation station:

```json
{
  "properties": {
    "temperature": {
      "value": 20.0,
      "unitCode": "wmoUnit:degC",
      "qualityControl": "V"
    },
    "dewpoint": {
      "value": 12.0,
      "unitCode": "wmoUnit:degC"
    },
    "windDirection": {
      "value": 180,
      "unitCode": "wmoUnit:degree_(angle)"
    },
    "windSpeed": {
      "value": 5.0,
      "unitCode": "wmoUnit:m_s-1"
    },
    "windGust": {
      "value": 8.0,
      "unitCode": "wmoUnit:m_s-1"
    },
    "barometricPressure": {
      "value": 101325.0,
      "unitCode": "wmoUnit:Pa"
    },
    "seaLevelPressure": {
      "value": 101325.0,
      "unitCode": "wmoUnit:Pa"
    },
    "visibility": {
      "value": 16093.0,
      "unitCode": "wmoUnit:m"
    },
    "relativeHumidity": {
      "value": 65.0,
      "unitCode": "wmoUnit:percent"
    },
    "heatIndex": {
      "value": 25.0,
      "unitCode": "wmoUnit:degC"
    },
    "cloudLayers": [
      {
        "base": {
          "value": 1000,
          "unitCode": "wmoUnit:m"
        },
        "amount": "FEW"
      }
    ],
    "textDescription": "Mostly Clear",
    "timestamp": "2024-01-15T14:30:00+00:00"
  }
}
```

### 3. Extended Forecast (Multiple Periods)

The forecast includes **14 periods** (7 days, day/night):

- Period 0: Current period
- Period 1-13: Future periods (up to 7 days ahead)
- Each period has all the fields listed above

### 4. Hourly Forecast

Available via: `grid_data['properties']['forecastHourly']`

Returns hourly forecasts for the next 7 days (168 hours).

### 5. Alerts

Available via: `grid_data['properties']['county']` → alerts endpoint

Weather warnings, watches, and advisories for your area.

## Additional Fields You Can Add

Here are useful fields not currently displayed:

### From Forecast:
- **`windDirection`**: "SW", "N", "NE", etc.
- **`dewpoint`**: Dew point temperature (°F)
- **`heatIndex`**: Feels-like temperature when hot
- **`windChill`**: Feels-like temperature when cold
- **`icon`**: URL to weather icon image
- **`isDaytime`**: Boolean (day vs night forecast)
- **`temperatureTrend`**: "rising", "falling", or null

### From Observations:
- **`windGust`**: Peak wind speed (mph)
- **`barometricPressure`**: Atmospheric pressure (Pa or inHg)
- **`visibility`**: Visibility distance (miles)
- **`cloudLayers`**: Cloud coverage details
- **`textDescription`**: Short weather description
- **`skyCover`**: Percentage of sky covered by clouds

### Extended Forecast:
- **Multiple periods**: Tomorrow, next week, etc.
- **High/Low temperatures**: Daily min/max
- **7-day forecast**: Full week ahead

## Example: Adding More Weather Data

To add more fields, modify `backend/app.py` in the `get_weather()` function:

```python
weather = {
    'temperature': round(temp, 1),
    'humidity': round(humidity, 1),
    'precipitation': current_period.get('probabilityOfPrecipitation', {}).get('value', 0),
    'windSpeed': round(wind_speed, 1),
    'windDirection': current_period.get('windDirection', 'N/A'),  # NEW
    'windGust': round(wind_gust, 1) if wind_gust else None,  # NEW
    'dewpoint': current_period.get('dewpoint', {}).get('value'),  # NEW
    'heatIndex': current_period.get('heatIndex', {}).get('value'),  # NEW
    'barometricPressure': obs_pressure if obs_pressure else None,  # NEW
    'visibility': obs_visibility if obs_visibility else None,  # NEW
    'forecast': current_period.get('shortForecast', 'Unknown'),
    'description': current_period.get('detailedForecast', ''),
    'icon': current_period.get('icon', ''),  # NEW
    'isDaytime': current_period.get('isDaytime', True),  # NEW
    'timestamp': datetime.now().isoformat()
}
```

## NWS API Endpoints Used

1. **Grid Point**: `https://api.weather.gov/points/{lat},{lon}`
   - Returns forecast URLs and station lists

2. **Forecast**: `grid_data['properties']['forecast']`
   - Returns 7-day forecast with periods

3. **Hourly Forecast**: `grid_data['properties']['forecastHourly']`
   - Returns hourly forecasts

4. **Observation Stations**: `grid_data['properties']['observationStations']`
   - Lists nearby weather stations

5. **Latest Observation**: `https://api.weather.gov/stations/{station_id}/observations/latest`
   - Real-time measurements from nearest station

## API Documentation

Full NWS API documentation:
- **Main API**: https://www.weather.gov/documentation/services-web-api
- **Forecast API**: https://api.weather.gov/openapi.json
- **Examples**: https://www.weather.gov/documentation/services-web-api#/

## Rate Limits

- **No API key required** (public API)
- **Rate limit**: ~5 requests per second per IP
- **User-Agent header required** (already set in your code)

## Units

- **Temperature**: Forecast in °F, Observations in °C (converted in code)
- **Wind Speed**: Forecast in mph (string), Observations in m/s (converted)
- **Pressure**: Pa (Pascals) - can convert to inHg or mb
- **Distance**: Meters (can convert to miles)

## Current Implementation Notes

- ✅ Uses forecast temperature (prefers observation if available)
- ✅ Uses observation humidity (more accurate)
- ✅ Uses forecast wind speed (parsed from string like "5 to 10 mph")
- ✅ Includes precipitation probability
- ✅ Includes short and detailed forecast text

## Potential Enhancements

1. **Add wind direction** (compass direction)
2. **Add dew point** (important for plant health)
3. **Add 7-day forecast** (show upcoming days)
4. **Add hourly forecast** (next 24 hours)
5. **Add weather alerts** (warnings for your area)
6. **Add UV index** (if available)
7. **Add sunrise/sunset times** (from forecast periods)
8. **Add cloud coverage** (percentage)
9. **Add barometric pressure** (trend indicator)

