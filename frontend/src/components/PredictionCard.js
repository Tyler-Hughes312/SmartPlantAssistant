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

  const hours = Math.round(prediction.hoursUntilWatering);
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;

  let wateringText = '';
  let icon = '💧';

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

  return (
    <div className="prediction-card">
      <div className="card-title">
        {icon} Watering Prediction
      </div>
      <div className="card-value">{wateringText}</div>
      <div className="card-label">
        Confidence: {Math.round(prediction.confidence * 100)}% | {prediction.recommendation || 'Monitoring...'}
      </div>
    </div>
  );
};

export default PredictionCard;

