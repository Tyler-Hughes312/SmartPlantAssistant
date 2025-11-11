#!/usr/bin/env python3
"""
Example script to show what raw weather data looks like from NWS API
Run this to see all available fields
"""

import requests
import json

# NWS API headers (required)
NWS_HEADERS = {
    'User-Agent': 'SmartPlantAssistant/1.0 (contact@example.com)',
    'Accept': 'application/json'
}

def get_weather_data(lat=40.7128, lon=-74.0060):
    """Fetch and display raw weather data"""
    
    print(f"Fetching weather for coordinates: {lat}, {lon}\n")
    print("=" * 70)
    
    # Step 1: Get grid point
    grid_url = f'https://api.weather.gov/points/{lat},{lon}'
    print(f"1. Grid Point URL: {grid_url}")
    grid_response = requests.get(grid_url, headers=NWS_HEADERS, timeout=10)
    
    if not grid_response.ok:
        print(f"   ❌ Error: {grid_response.status_code}")
        return
    
    grid_data = grid_response.json()
    print(f"   ✅ Success")
    print(f"   Grid ID: {grid_data['properties']['gridId']}")
    print(f"   Grid X: {grid_data['properties']['gridX']}")
    print(f"   Grid Y: {grid_data['properties']['gridY']}")
    print()
    
    # Step 2: Get forecast
    forecast_url = grid_data['properties']['forecast']
    print(f"2. Forecast URL: {forecast_url}")
    forecast_response = requests.get(forecast_url, headers=NWS_HEADERS, timeout=10)
    
    if not forecast_response.ok:
        print(f"   ❌ Error: {forecast_response.status_code}")
        return
    
    forecast_data = forecast_response.json()
    print(f"   ✅ Success")
    print(f"   Number of periods: {len(forecast_data['properties']['periods'])}")
    print()
    
    # Show current period (period 0)
    current_period = forecast_data['properties']['periods'][0]
    print("=" * 70)
    print("CURRENT PERIOD (Period 0) - All Available Fields:")
    print("=" * 70)
    print(json.dumps(current_period, indent=2))
    print()
    
    # Step 3: Get observation stations
    observation_url = grid_data['properties']['observationStations']
    print("=" * 70)
    print(f"3. Observation Stations URL: {observation_url}")
    stations_response = requests.get(observation_url, headers=NWS_HEADERS, timeout=10)
    
    if stations_response.ok:
        stations_data = stations_response.json()
        if stations_data.get('features') and len(stations_data['features']) > 0:
            station_id = stations_data['features'][0]['properties']['stationIdentifier']
            print(f"   ✅ Found station: {station_id}")
            
            # Get latest observation
            obs_url = f'https://api.weather.gov/stations/{station_id}/observations/latest'
            print(f"4. Latest Observation URL: {obs_url}")
            obs_response = requests.get(obs_url, headers=NWS_HEADERS, timeout=10)
            
            if obs_response.ok:
                observation_data = obs_response.json()
                print("   ✅ Success")
                print()
                print("=" * 70)
                print("LATEST OBSERVATION - All Available Fields:")
                print("=" * 70)
                print(json.dumps(observation_data['properties'], indent=2))
            else:
                print(f"   ❌ Error: {obs_response.status_code}")
        else:
            print("   ⚠️  No observation stations found")
    else:
        print(f"   ❌ Error: {stations_response.status_code}")
    
    print()
    print("=" * 70)
    print("SUMMARY - What Your App Currently Uses:")
    print("=" * 70)
    
    # Show what your app extracts
    temp = current_period['temperature']
    humidity = current_period.get('relativeHumidity', {}).get('value', 60)
    precipitation = current_period.get('probabilityOfPrecipitation', {}).get('value', 0)
    wind_speed_str = current_period.get('windSpeed', '5 mph')
    forecast = current_period.get('shortForecast', 'Unknown')
    description = current_period.get('detailedForecast', '')
    
    print(f"Temperature: {temp}°F")
    print(f"Humidity: {humidity}%")
    print(f"Precipitation Probability: {precipitation}%")
    print(f"Wind Speed: {wind_speed_str}")
    print(f"Forecast: {forecast}")
    print(f"Description: {description[:100]}...")
    print()
    
    print("=" * 70)
    print("ADDITIONAL FIELDS AVAILABLE (Not Currently Used):")
    print("=" * 70)
    print(f"Wind Direction: {current_period.get('windDirection', 'N/A')}")
    print(f"Dewpoint: {current_period.get('dewpoint', {}).get('value', 'N/A')}°F")
    print(f"Heat Index: {current_period.get('heatIndex', {}).get('value', 'N/A')}°F")
    print(f"Wind Chill: {current_period.get('windChill', {}).get('value', 'N/A')}°F")
    print(f"Temperature Trend: {current_period.get('temperatureTrend', 'N/A')}")
    print(f"Is Daytime: {current_period.get('isDaytime', 'N/A')}")
    print(f"Icon URL: {current_period.get('icon', 'N/A')}")
    print()
    
    # Show extended forecast periods
    print("=" * 70)
    print("EXTENDED FORECAST (Next Few Periods):")
    print("=" * 70)
    for i, period in enumerate(forecast_data['properties']['periods'][:5]):
        print(f"\nPeriod {i}: {period.get('name', 'Unknown')}")
        print(f"  Temperature: {period.get('temperature', 'N/A')}°F")
        print(f"  Forecast: {period.get('shortForecast', 'N/A')}")
        print(f"  Wind: {period.get('windSpeed', 'N/A')} {period.get('windDirection', '')}")

if __name__ == '__main__':
    # Default to NYC, but you can change these
    latitude = 40.7128  # New York City
    longitude = -74.0060
    
    # Uncomment to use your location:
    # latitude = YOUR_LATITUDE
    # longitude = YOUR_LONGITUDE
    
    get_weather_data(latitude, longitude)

