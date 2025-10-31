import React from 'react';
import './SensorDashboard.css';

const SensorDashboard = ({ sensorData }) => {
  if (!sensorData) {
    return <div className="dashboard">Loading sensor data...</div>;
  }

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
        <div className="card-label">Current ambient light</div>
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
        <div className="card-label">Soil moisture level</div>
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
        <div className="card-label">Current temperature</div>
      </div>
    </div>
  );
};

export default SensorDashboard;

