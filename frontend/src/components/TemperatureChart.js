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

const TemperatureChart = ({ history }) => {
  // ALL HOOKS MUST BE CALLED BEFORE ANY EARLY RETURNS (React hooks rule)
  
  // Calculate stable y-axis range (memoized to prevent constant recalculation)
  const { suggestedMin, suggestedMax } = useMemo(() => {
    if (!history || history.length === 0) {
      return { suggestedMin: 60, suggestedMax: 80 };
    }
    const tempValues = history.map((item) => item.temperature).filter(val => val != null);
    if (tempValues.length === 0) {
      return { suggestedMin: 60, suggestedMax: 80 };
    }
    const minTemp = Math.min(...tempValues);
    const maxTemp = Math.max(...tempValues);
    
    // Calculate stable range with padding (15% padding on each side)
    const range = maxTemp - minTemp;
    const padding = Math.max(range * 0.15, 5); // At least 5°F padding
    return {
      suggestedMin: Math.floor(minTemp - padding),
      suggestedMax: Math.ceil(maxTemp + padding)
    };
  }, [
    // Only recalculate when min/max values change significantly (rounded to nearest 5°F)
    history?.length > 0 ? Math.floor((Math.min(...history.map(h => h.temperature).filter(v => v != null)) || 60) / 5) : null,
    history?.length > 0 ? Math.floor((Math.max(...history.map(h => h.temperature).filter(v => v != null)) || 80) / 5) : null
  ]);

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
          label: 'Temperature (°F)',
          data: history.map((item) => item.temperature),
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    };
  }, [labels, history?.map(h => h.temperature).join(',')]);

  // NOW we can do early returns
  if (!history || history.length === 0 || !chartData) {
    return (
      <div className="chart-container">
        <div className="chart-title">🌡️ Temperature Over Time</div>
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
        beginAtZero: false,
        min: suggestedMin,
        max: suggestedMax,
        title: {
          display: true,
          text: 'Temperature (°F)',
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
            return `Temperature: ${context.parsed.y.toFixed(1)}°F`;
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">🌡️ Temperature Over Time</div>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default memo(TemperatureChart);

