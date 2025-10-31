import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  fetchSensorData,
  fetchWeather,
  fetchPrediction,
  getPlants,
  createPlant,
  deletePlant,
  getSensorHistory,
  getPlantHealth
} from '../services/api';
import SensorDashboard from './SensorDashboard';
import WeatherSection from './WeatherSection';
import PredictionCard from './PredictionCard';
import SensorChart from './SensorChart';
import PredictionChart from './PredictionChart';
import PlantManagement from './PlantManagement';
import PlantHealthScore from './PlantHealthScore';
import Chatbot from './Chatbot';
import LocationSettings from './LocationSettings';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [sensorData, setSensorData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [plants, setPlants] = useState([]);
  const [selectedPlantId, setSelectedPlantId] = useState(null);
  const [selectedPlant, setSelectedPlant] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPlants();
  }, []);

  useEffect(() => {
    if (plants.length > 0 && !selectedPlantId) {
      setSelectedPlantId(plants[0].id);
    }
  }, [plants, selectedPlantId]);

  useEffect(() => {
    if (selectedPlantId) {
      loadData();
      const interval = setInterval(loadData, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedPlantId]);

  useEffect(() => {
    // Weather will be loaded with user's saved location or geolocation
    updateWeather();
  }, []);

  const loadPlants = async () => {
    try {
      const plantsData = await getPlants();
      setPlants(plantsData);
      if (plantsData.length === 0) {
        setError('No plants found. Please add a plant first.');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error loading plants:', err);
      setError('Failed to load plants');
      setLoading(false);
    }
  };

  const loadData = async () => {
    if (!selectedPlantId) return;

    try {
      setError(null);
      const [sensor, historyData] = await Promise.all([
        fetchSensorData(selectedPlantId),
        getSensorHistory(selectedPlantId, 20)
      ]);

      setSensorData(sensor);
      setSelectedPlant(plants.find(p => p.id === selectedPlantId));
      setHistory(historyData.map(h => ({
        ...h,
        timestamp: new Date(h.timestamp),
        prediction: null // Will be updated with prediction
      })));

      // Get weather if not loaded
      if (!weatherData) {
        await updateWeather();
      }

      // Get prediction and health data
      if (sensor && weatherData) {
        const pred = await fetchPrediction(sensor, weatherData);
        setPrediction(pred);
        
        // Try to get health data (may fail if no readings yet)
        try {
          const health = await getPlantHealth(selectedPlantId);
          setHealthData(health);
        } catch (err) {
          // No health data yet - that's okay for new plants
          setHealthData(null);
        }

        // Update history with prediction
        setHistory(prev => {
          const updated = [...prev];
          if (updated.length > 0) {
            updated[updated.length - 1] = {
              ...updated[updated.length - 1],
              prediction: pred.hoursUntilWatering,
              confidence: pred.confidence
            };
          }
          return updated;
        });
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.response?.data?.error || err.message);
      setLoading(false);
    }
  };

  const updateWeather = async (lat = null, lon = null) => {
    try {
      const weather = await fetchWeather(lat, lon);
      setWeatherData(weather);

      // Update prediction if we have sensor data
      if (sensorData) {
        const pred = await fetchPrediction(sensorData, weather);
        setPrediction(pred);
      }
    } catch (err) {
      console.error('Error updating weather:', err);
    }
  };

  const handlePlantCreated = async (plant) => {
    await loadPlants();
    setSelectedPlantId(plant.id);
  };

  const handlePlantDeleted = async () => {
    await loadPlants();
    if (plants.length > 1) {
      const remainingPlants = await getPlants();
      if (remainingPlants.length > 0) {
        setSelectedPlantId(remainingPlants[0].id);
      } else {
        setSelectedPlantId(null);
        setError('No plants found. Please add a plant first.');
      }
    } else {
      setSelectedPlantId(null);
      setSensorData(null);
      setHistory([]);
      setError('No plants found. Please add a plant first.');
    }
  };

  if (loading && plants.length === 0) {
    return (
      <div className="app-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="header">
        <div className="header-content">
          <div className="header-logo-section">
            <img 
              src="/logo.png" 
              alt="S-PLANT Pledge Project" 
              className="header-logo"
            />
          </div>
          <div className="user-info">
            <span>Welcome, {user?.username}</span>
            <button onClick={logout} className="logout-button">Logout</button>
          </div>
        </div>
      </div>

      <PlantManagement
        plants={plants}
        selectedPlantId={selectedPlantId}
        onPlantSelect={setSelectedPlantId}
        onPlantCreated={handlePlantCreated}
        onPlantDeleted={handlePlantDeleted}
      />

      {error && plants.length === 0 && (
        <div className="error-banner">{error}</div>
      )}

      {selectedPlantId && !error && (
        <div className="content">
          {/* Sensor Data - Full Width Horizontal Row */}
          <SensorDashboard sensorData={sensorData} />

          {/* Main Dashboard Grid */}
          <div className="main-dashboard-grid">
            {/* Left Column: Weather */}
            <div className="left-column">
              <WeatherSection weatherData={weatherData} />
            </div>

            {/* Right Column: Plant Health and Prediction */}
            <div className="right-column">
              <PlantHealthScore plantId={selectedPlantId} />
              <PredictionCard prediction={prediction} />
            </div>
          </div>

          {/* Charts Section */}
          <div className="charts-section">
            <SensorChart history={history} />
            <PredictionChart history={history} />
          </div>

          {/* Chatbot Section */}
          <div className="chatbot-section">
            <Chatbot 
              sensorData={sensorData}
              weatherData={weatherData}
              healthData={healthData}
              plantName={selectedPlant?.name}
            />
          </div>
        </div>
      )}

      {/* Location Settings at Bottom */}
      <LocationSettings />
    </div>
  );
};

export default Dashboard;

