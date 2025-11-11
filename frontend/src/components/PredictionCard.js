import React from 'react';
import './PredictionCard.css';

const PredictionCard = ({ prediction }) => {
  if (!prediction) {
    return (
      <div className="prediction-card">
        <div className="card-title">💧 Watering Prediction</div>
        <div className="card-value">Loading...</div>
      </div>
    );
  }

  let wateringText = '';
  let icon = '💧';
  let statusBadge = '';

  // Check if we have moisture data or frequency data
  if (prediction.hasMoistureData && prediction.hoursUntilWatering !== undefined) {
    // Has moisture data - show hours until watering
    statusBadge = <span className="moisture-badge">🌱 With Moisture Sensor</span>;
    
    const hours = Math.round(prediction.hoursUntilWatering);
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;

    if (days > 0) {
      wateringText = `${days} day${days > 1 ? 's' : ''}`;
      if (remainingHours > 0) {
        wateringText += ` ${remainingHours} hour${remainingHours > 1 ? 's' : ''}`;
      }
    } else {
      wateringText = `${remainingHours} hour${remainingHours > 1 ? 's' : ''}`;
    }

    if (hours < 24) {
      wateringText = `⚠️ Water soon! In ${wateringText}`;
      icon = '⚠️';
    } else if (hours < 48) {
      wateringText = `💧 Water in ${wateringText}`;
    } else {
      wateringText = `✅ Water in ${wateringText}`;
      icon = '✅';
    }
  } else if (prediction.wateringFrequencyDays !== undefined) {
    // No moisture data - show watering frequency
    statusBadge = <span className="weather-badge">🌤️ Weather-Based</span>;
    
    const frequencyDays = prediction.wateringFrequencyDays;
    
    if (frequencyDays < 1.5) {
      const hours = Math.round(frequencyDays * 24);
      wateringText = `💧 Water every ${hours} hour${hours !== 1 ? 's' : ''}`;
      icon = '💧';
    } else if (frequencyDays < 2) {
      wateringText = `💧 Water every ${Math.round(frequencyDays)} day`;
      icon = '💧';
    } else {
      wateringText = `💧 Water every ${Math.round(frequencyDays)} days`;
      icon = '💧';
    }
  } else {
    wateringText = 'No prediction available';
  }

  return (
    <div className="prediction-card">
      <div className="card-title">
        {icon} Watering {prediction.hasMoistureData ? 'Prediction' : 'Frequency'}
        {statusBadge}
      </div>
      <div className="card-value">{wateringText}</div>
      <div className="card-label">
        {prediction.recommendation || 'Monitoring...'}
      </div>
    </div>
  );
};

export default PredictionCard;

