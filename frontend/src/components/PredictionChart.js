import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import './Chart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const PredictionChart = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-title">Watering Prediction Confidence</div>
        <div className="no-data">No prediction data available yet...</div>
      </div>
    );
  }

  const labels = history.map((item) => {
    const date = new Date(item.timestamp);
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  });

  const data = {
    labels,
    datasets: [
      {
        label: 'Hours Until Watering',
        data: history.map((item) => item.prediction),
        backgroundColor: 'rgba(139, 92, 246, 0.6)',
        borderColor: '#8b5cf6',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Hours',
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
            const confidence = history[context.dataIndex]?.confidence || 0;
            return `Hours: ${context.parsed.y.toFixed(1)} | Confidence: ${Math.round(confidence * 100)}%`;
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">Watering Prediction Over Time</div>
      <div className="chart-wrapper">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default PredictionChart;

