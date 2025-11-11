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

const MoistureChart = ({ history }) => {
  // ALL HOOKS MUST BE CALLED BEFORE ANY EARLY RETURNS (React hooks rule)
  
  // Memoize labels and data to prevent recalculation on every render
  const labels = useMemo(() => {
    if (!history || history.length === 0) return [];
    return history.map((item) => {
      const date = new Date(item.timestamp);
      return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
    });
  }, [history?.map(h => h.timestamp?.getTime()).join(',')]);

  const chartData = useMemo(() => {
    if (!history || history.length === 0) return null;
    return {
      labels,
      datasets: [
        {
          label: 'Moisture (%)',
          data: history.map((item) => item.moisture),
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    };
  }, [labels, history?.map(h => h.moisture).join(',')]);

  // NOW we can do early returns
  if (!history || history.length === 0 || !chartData) {
    return (
      <div className="chart-container">
        <div className="chart-title">💧 Soil Moisture Over Time</div>
        <div className="no-data">No data available yet. Collecting sensor readings...</div>
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
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Moisture (%)',
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
            return `Moisture: ${context.parsed.y.toFixed(1)}%`;
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">💧 Soil Moisture Over Time</div>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default memo(MoistureChart);

