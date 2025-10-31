import React from 'react';
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

const SensorChart = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div className="chart-container">
        <div className="chart-title">Sensor Data Over Time</div>
        <div className="no-data">No data available yet. Collecting sensor readings...</div>
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
        label: 'Light (lux)',
        data: history.map((item) => item.light),
        borderColor: '#fbbf24',
        backgroundColor: 'rgba(251, 191, 36, 0.1)',
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'Moisture (%)',
        data: history.map((item) => item.moisture),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        yAxisID: 'y1',
      },
      {
        label: 'Temperature (°F)',
        data: history.map((item) => item.temperature),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        yAxisID: 'y2',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Light (lux)',
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Moisture (%)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
      y2: {
        type: 'linear',
        display: false,
        position: 'right',
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">Sensor Data Over Time</div>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default SensorChart;

