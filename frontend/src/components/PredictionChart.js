import React, { useMemo, memo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import './Chart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const PredictionChart = ({ history }) => {
  // Calculate stable y-axis range (memoized to prevent constant recalculation)
  // Must be called before any early returns (React hooks rule)
  const { suggestedMin, suggestedMax, predictionData, labels } = useMemo(() => {
    if (!history || history.length === 0) {
      return { 
        suggestedMin: 0, 
        suggestedMax: 168, // 7 days in hours
        predictionData: [],
        labels: []
      };
    }

    // Convert predictions to consistent units (hours)
    // If prediction is > 48, assume it's in days and convert to hours
    // Otherwise, assume it's already in hours
    const labels = history.map((item) => {
      const date = new Date(item.timestamp);
      const month = date.getMonth() + 1;
      const day = date.getDate();
      const hours = date.getHours();
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${month}/${day} ${hours}:${minutes}`;
    });

    const predictionData = history.map((item) => {
      // If prediction is > 48, it's likely in days (convert to hours)
      // Otherwise, it's already in hours
      return item.prediction > 48 ? item.prediction * 24 : item.prediction;
    });

    // Calculate stable range with padding (15% padding on each side)
    const minPred = Math.min(...predictionData);
    const maxPred = Math.max(...predictionData);
    const range = maxPred - minPred;
    const padding = Math.max(range * 0.15, 12); // At least 12 hours padding
    const suggestedMin = Math.max(0, Math.floor(minPred - padding));
    const suggestedMax = Math.ceil(maxPred + padding);

    return {
      suggestedMin,
      suggestedMax,
      predictionData,
      labels
    };
  }, [
    // Only recalculate when min/max values change significantly (rounded to nearest 12 hours)
    history.length > 0 ? Math.floor((Math.min(...history.map(h => h.prediction > 48 ? h.prediction * 24 : h.prediction)) || 0) / 12) : null,
    history.length > 0 ? Math.floor((Math.max(...history.map(h => h.prediction > 48 ? h.prediction * 24 : h.prediction)) || 168) / 12) : null
  ]);

  // Determine if we have moisture data (check if any prediction has moisture data)
  const hasMoistureData = useMemo(() => {
    if (!history || history.length === 0) return false;
    return history.some(item => item.hasMoistureData);
  }, [history?.map(h => h.hasMoistureData).join(',')]);

  const chartData = useMemo(() => {
    if (!history || history.length === 0 || !labels || predictionData.length === 0) return null;
    return {
      labels,
      datasets: [
        {
          label: hasMoistureData ? 'Hours Until Watering (with sensor)' : 'Watering Frequency (weather-based)',
          data: predictionData,
          backgroundColor: hasMoistureData 
            ? 'rgba(76, 175, 80, 0.1)' 
            : 'rgba(139, 92, 246, 0.1)',
          borderColor: hasMoistureData ? '#4caf50' : '#8b5cf6',
          borderWidth: 2,
          pointBackgroundColor: hasMoistureData ? '#4caf50' : '#8b5cf6',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.3, // Smooth curve
          fill: true,
        },
      ],
    };
  }, [labels, predictionData?.join(','), hasMoistureData]);

  // NOW we can do early returns
  if (!history || history.length === 0 || !chartData) {
    return (
      <div className="chart-container">
        <div className="chart-title">💧 Watering Prediction Over Time</div>
        <div className="no-data">No prediction data available yet. Predictions will appear here as they are generated.</div>
      </div>
    );
  }

  const data = chartData;

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      y: {
        beginAtZero: true,
        min: suggestedMin,
        max: suggestedMax,
        title: {
          display: true,
          text: hasMoistureData ? 'Hours Until Watering' : 'Hours (Frequency)',
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const hours = context.parsed.y;
            const item = history[context.dataIndex];
            
            if (item.hasMoistureData) {
              // With moisture sensor - show hours until watering
              if (hours >= 24) {
                const days = (hours / 24).toFixed(1);
                return `${days} days (${hours.toFixed(1)} hours) until watering`;
              }
              return `${hours.toFixed(1)} hours until watering`;
            } else {
              // Weather-based - show frequency
              if (hours >= 24) {
                const days = (hours / 24).toFixed(1);
                return `Water every ${days} days (${hours.toFixed(1)} hours)`;
              }
              return `Water every ${hours.toFixed(1)} hours`;
            }
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">
        💧 Watering Prediction Over Time
        {hasMoistureData && (
          <span style={{ fontSize: '0.8em', color: '#4caf50', marginLeft: '10px' }}>
            🌱 With Moisture Sensor
          </span>
        )}
        {!hasMoistureData && (
          <span style={{ fontSize: '0.8em', color: '#8b5cf6', marginLeft: '10px' }}>
            🌤️ Weather-Based
          </span>
        )}
      </div>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default memo(PredictionChart);

