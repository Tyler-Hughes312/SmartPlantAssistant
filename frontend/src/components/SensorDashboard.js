import React from 'react';
import './SensorDashboard.css';

const SensorDashboard = ({ sensorData }) => {
  // Only show real data from Neon database
  if (!sensorData) {
    return (
      <div className="dashboard">
        <div className="no-data-message">Waiting for sensor data from Raspberry Pi...</div>
      </div>
    );
  }

  // Check if data is simulated (shouldn't happen anymore, but double-check)
  if (sensorData.is_simulated) {
    return (
      <div className="dashboard">
        <div className="no-data-message">Waiting for real sensor data from Raspberry Pi...</div>
      </div>
    );
  }

  // Check if we have real values (not null/undefined)
  const hasRealData = sensorData.light != null && 
                      sensorData.moisture != null && 
                      sensorData.temperature != null;

  if (!hasRealData) {
    return (
      <div className="dashboard">
        <div className="no-data-message">
          {sensorData.message || 'Waiting for sensor data from Raspberry Pi...'}
        </div>
      </div>
    );
  }

  // Only display real data from Neon database
  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-title">
          <span className="status-indicator active"></span>
          Light Level
        </div>
        <div className="card-value">
          {Math.round(sensorData.light)}
          <span className="card-unit"> lux</span>
        </div>
        <div className="card-label">Current ambient light (from Raspberry Pi)</div>
      </div>

      <div className="card">
        <div className="card-title">
          <span className="status-indicator active"></span>
          Soil Moisture
        </div>
        <div className="card-value">
          {Math.round(sensorData.moisture)}
          <span className="card-unit">%</span>
        </div>
        <div className="card-label">Soil moisture level (from Raspberry Pi)</div>
      </div>

      <div className="card">
        <div className="card-title">
          <span className="status-indicator active"></span>
          Temperature
        </div>
        <div className="card-value">
          {Math.round(sensorData.temperature)}
          <span className="card-unit">°F</span>
        </div>
        <div className="card-label">Current temperature (from Raspberry Pi)</div>
      </div>
    </div>
  );
};

export default SensorDashboard;

