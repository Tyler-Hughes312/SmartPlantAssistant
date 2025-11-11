import React from 'react';
import './WeatherSection.css';

const WeatherSection = ({ weatherData }) => {
  if (!weatherData) {
    return (
      <div className="weather-section">
        <div className="card-title">🌤️ National Weather Service Data</div>
        <div className="loading-weather">Loading weather data...</div>
      </div>
    );
  }

  // Check if weather data has an error
  if (weatherData.error) {
    return (
      <div className="weather-section">
        <div className="card-title">🌤️ National Weather Service Data</div>
        <div className="weather-error">
          {weatherData.message || weatherData.error}
          <br />
          <small>Please check your location settings.</small>
        </div>
      </div>
    );
  }

  return (
    <div className="weather-section">
      <div className="card-title">🌤️ National Weather Service Data</div>
      <div className="weather-grid">
        <div className="weather-item">
          <div className="weather-item-label">Temperature</div>
          <div className="weather-item-value">
            {weatherData.temperature != null ? `${Math.round(weatherData.temperature)}°F` : 'N/A'}
          </div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Humidity</div>
          <div className="weather-item-value">
            {weatherData.humidity != null ? `${Math.round(weatherData.humidity)}%` : 'N/A'}
          </div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Precipitation</div>
          <div className="weather-item-value">
            {weatherData.precipitation != null ? `${weatherData.precipitation}%` : 'N/A'}
          </div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Wind Speed</div>
          <div className="weather-item-value">
            {weatherData.windSpeed != null ? `${weatherData.windSpeed} mph` : 'N/A'}
          </div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Forecast</div>
          <div className="weather-item-value forecast-text">
            {weatherData.forecast || 'N/A'}
          </div>
        </div>
      </div>
      {weatherData.description && (
        <div className="weather-description">{weatherData.description}</div>
      )}
    </div>
  );
};

export default WeatherSection;

