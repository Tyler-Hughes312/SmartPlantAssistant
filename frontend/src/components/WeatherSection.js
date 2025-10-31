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

  return (
    <div className="weather-section">
      <div className="card-title">🌤️ National Weather Service Data</div>
      <div className="weather-grid">
        <div className="weather-item">
          <div className="weather-item-label">Temperature</div>
          <div className="weather-item-value">{Math.round(weatherData.temperature)}°F</div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Humidity</div>
          <div className="weather-item-value">{Math.round(weatherData.humidity)}%</div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Precipitation</div>
          <div className="weather-item-value">{weatherData.precipitation}%</div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Wind Speed</div>
          <div className="weather-item-value">{weatherData.windSpeed} mph</div>
        </div>
        <div className="weather-item">
          <div className="weather-item-label">Forecast</div>
          <div className="weather-item-value forecast-text">{weatherData.forecast}</div>
        </div>
      </div>
      {weatherData.description && (
        <div className="weather-description">{weatherData.description}</div>
      )}
    </div>
  );
};

export default WeatherSection;

