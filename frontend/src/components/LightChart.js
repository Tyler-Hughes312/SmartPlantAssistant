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

const LightChart = ({ history }) => {
  // ALL HOOKS MUST BE CALLED BEFORE ANY EARLY RETURNS (React hooks rule)
  
  // Calculate stable y-axis range (memoized to prevent constant recalculation)
  const { suggestedMin, suggestedMax } = useMemo(() => {
    if (!history || history.length === 0) {
      return { suggestedMin: 0, suggestedMax: 1000 };
    }
    const lightValues = history.map((item) => item.light).filter(val => val != null);
    if (lightValues.length === 0) {
      return { suggestedMin: 0, suggestedMax: 1000 };
    }
    const minLight = Math.min(...lightValues);
    const maxLight = Math.max(...lightValues);
    
    // Calculate stable range with padding (20% padding on each side)
    const range = maxLight - minLight;
    const padding = Math.max(range * 0.2, 50); // At least 50 lux padding
    return {
      suggestedMin: Math.max(0, Math.floor(minLight - padding)),
      suggestedMax: Math.ceil(maxLight + padding)
    };
  }, [
    // Only recalculate when min/max values change significantly (rounded to nearest 50)
    history?.length > 0 ? Math.floor((Math.min(...history.map(h => h.light).filter(v => v != null)) || 0) / 50) : null,
    history?.length > 0 ? Math.floor((Math.max(...history.map(h => h.light).filter(v => v != null)) || 1000) / 50) : null
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
          label: 'Light (lux)',
          data: history.map((item) => item.light),
          borderColor: '#fbbf24',
          backgroundColor: 'rgba(251, 191, 36, 0.1)',
          tension: 0.4,
          fill: true,
        },
      ],
    };
  }, [labels, history?.map(h => h.light).join(',')]);

  // NOW we can do early returns
  if (!history || history.length === 0 || !chartData) {
    return (
      <div className="chart-container">
        <div className="chart-title">💡 Light Level Over Time</div>
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
        min: suggestedMin,
        max: suggestedMax,
        title: {
          display: true,
          text: 'Light (lux)',
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
            return `Light: ${context.parsed.y.toFixed(1)} lux`;
          },
        },
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-title">💡 Light Level Over Time</div>
      <div className="chart-wrapper">
        <Line data={data} options={options} />
      </div>
    </div>
  );
};

export default memo(LightChart);

