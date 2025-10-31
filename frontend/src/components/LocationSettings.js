import React, { useState, useEffect } from 'react';
import { updateUserLocation, getCurrentUser } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './LocationSettings.css';

const LocationSettings = () => {
  const { checkAuth } = useAuth();
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUserLocation();
  }, []);

  const loadUserLocation = async () => {
    try {
      const user = await getCurrentUser();
      if (user.location) {
        setLocation(user.location);
      }
    } catch (err) {
      console.error('Error loading user location:', err);
    }
  };

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      setLoading(true);
      setError('');
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            // Reverse geocode to get place name
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`,
              { headers: { 'User-Agent': 'SmartPlantAssistant' } }
            );
            const data = await response.json();
            if (data && data.address) {
              const addr = data.address;
              let placeName = '';
              if (addr.city) {
                placeName = addr.city;
                if (addr.state) placeName += `, ${addr.state}`;
                else if (addr.country) placeName += `, ${addr.country}`;
              } else if (addr.town) {
                placeName = addr.town;
                if (addr.state) placeName += `, ${addr.state}`;
                else if (addr.country) placeName += `, ${addr.country}`;
              } else {
                placeName = data.display_name.split(',')[0] + (addr.state ? `, ${addr.state}` : '');
              }
              setLocation(placeName);
            } else {
              setLocation(`${lat.toFixed(4)}, ${lon.toFixed(4)}`);
            }
          } catch (err) {
            // Fallback to coordinates
            setLocation(`${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`);
          }
          setLoading(false);
        },
        (err) => {
          setError('Could not get your location. Please enter your city manually.');
          setLoading(false);
        }
      );
    } else {
      setError('Geolocation is not supported by your browser.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!location || !location.trim()) {
      setError('Please enter a location (e.g., "Nashville, TN" or "New York, NY")');
      return;
    }

    setLoading(true);
    try {
      await updateUserLocation(location.trim());
      setSuccess(true);
      await checkAuth(); // Refresh user data
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update location');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="location-settings">
      <h3>📍 Location</h3>
      
      <form onSubmit={handleSubmit}>
        <button
          type="button"
          onClick={handleGetCurrentLocation}
          disabled={loading}
          className="location-button"
        >
          {loading ? 'Getting location...' : '📍 Current'}
        </button>

        <div className="location-form-group">
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="City, State (e.g., Nashville, TN)"
            autoComplete="address-level2"
            required
          />
        </div>

        <button type="submit" disabled={loading} className="location-submit-button">
          {loading ? 'Saving...' : 'Save'}
        </button>

        {error && <div className="location-error">{error}</div>}
        {success && <div className="location-success">✅ Saved</div>}
      </form>

      {location && !error && !success && (
        <div className="location-info">
          <p><strong>{location}</strong></p>
        </div>
      )}
    </div>
  );
};

export default LocationSettings;

