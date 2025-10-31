import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Auth.css';

const Register = ({ onSwitchToLogin }) => {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [location, setLocation] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    const result = await register(username, email, password, location);
    setLoading(false);

    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-wrapper">
        <div className="auth-card">
          <div className="auth-header-section">
            <h1>🌱 Smart Plant Assistant</h1>
            <p className="auth-subtitle">Start monitoring your plants today</p>
          </div>
          
          <div className="auth-form-section">
            <h2>Create Your Account</h2>
            <form onSubmit={handleSubmit}>
              {error && <div className="error-message">{error}</div>}
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                  placeholder="Choose a username"
                />
                <small className="form-help">This will be your unique identifier</small>
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  placeholder="your.email@example.com"
                />
                <small className="form-help">We'll never share your email</small>
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                  minLength={6}
                  placeholder="At least 6 characters"
                />
                <small className="form-help">Minimum 6 characters</small>
              </div>
              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                  minLength={6}
                  placeholder="Re-enter your password"
                />
              </div>

              <div className="form-divider">
                <span>Location (for accurate weather)</span>
              </div>

              <div className="form-group">
                <label>City/Location</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g., Nashville, TN or New York, NY"
                  autoComplete="address-level2"
                />
                <small className="form-help">Enter your city and state/country (e.g., "Nashville, TN" or "London, UK")</small>
              </div>

              <div className="form-group">
                <button
                  type="button"
                  onClick={() => {
                    if (navigator.geolocation) {
                      setError('');
                      navigator.geolocation.getCurrentPosition(
                        async (position) => {
                          // Reverse geocode to get place name
                          try {
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
                        },
                        () => {
                          setError('Could not get your location. Please enter your city manually.');
                        }
                      );
                    } else {
                      setError('Geolocation not supported. Please enter your city manually.');
                    }
                  }}
                  className="location-button"
                >
                  📍 Use My Current Location
                </button>
              </div>

              <button type="submit" disabled={loading} className="auth-button">
                {loading ? 'Creating Account...' : 'Create Account'}
              </button>
            </form>
            <p className="auth-switch">
              Already have an account?{' '}
              <button type="button" onClick={onSwitchToLogin} className="link-button">
                Sign In
              </button>
            </p>
          </div>

          <div className="auth-info-section">
            <h3>What You'll Get</h3>
            <ul className="auth-features">
              <li>📊 Monitor sensor data (light, moisture, temperature)</li>
              <li>🌤️ Real-time weather from NWS</li>
              <li>💧 ML-powered watering predictions</li>
              <li>📈 Plant health scoring system</li>
              <li>💬 AI chatbot for plant care advice</li>
              <li>📍 Custom location for accurate weather</li>
            </ul>
            <div className="auth-note">
              <p>💡 <strong>Tip:</strong> After registering, set your location in the dashboard for accurate weather data!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

