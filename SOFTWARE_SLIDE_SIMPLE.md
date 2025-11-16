# Smart Plant Assistant
## IoT Plant Monitoring System with AI-Powered Care Recommendations

---

## 🎯 Overview

**Full-stack IoT application** that monitors plant health using Raspberry Pi sensors and provides intelligent care recommendations through machine learning and AI.

---

## 🏗️ System Architecture

```
Raspberry Pi Sensors → Flask API → Neon Postgres → React Dashboard
     (IoT)              (Backend)     (Database)      (Frontend)
```

**Hardware**: AHT20 (temp/humidity), BH1750 (light), Arduino (soil moisture)  
**Software**: Flask (Python), React (JavaScript), PostgreSQL (Neon)  
**AI/ML**: Random Forest models + GPT-4 chatbot

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| **Real-Time Monitoring** | Sensor readings every 10 seconds |
| **ML Predictions** | Watering predictions & health scoring |
| **AI Chatbot** | GPT-4 powered assistant with live sensor context |
| **Data Visualization** | Interactive charts for trends & history |
| **Multi-Plant Support** | Manage multiple plants per user |

---

## 🤖 Machine Learning

- **Random Forest Regressor**: Predicts hours until watering (6-168 hours)
- **Random Forest Classifier**: Classifies plant health (Excellent → Critical)
- **Features**: Temperature, humidity, precipitation, soil moisture, trends

---

## 📊 Data Flow

1. Sensors read data → 2. Raspberry Pi sends to API → 3. Stored in Postgres → 4. ML models generate predictions → 5. Frontend displays + AI chatbot uses data

---

## 🔑 Key Technologies

**Backend**: Flask, SQLAlchemy, scikit-learn, OpenAI API  
**Frontend**: React, Chart.js, Axios  
**Database**: Neon Postgres (cloud)  
**Hardware**: Raspberry Pi + I2C sensors

---

## 💡 Innovation

✅ Real-time IoT integration with physical sensors  
✅ Hybrid ML (sensor data + weather predictions)  
✅ Context-aware AI chatbot using live sensor data  
✅ Cloud-native scalable architecture  
✅ End-to-end solution: hardware → web interface

---

## 🎯 Result

**Automated plant care monitoring** with intelligent, data-driven recommendations powered by real-time sensor data and machine learning.


