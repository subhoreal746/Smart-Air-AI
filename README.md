# 🧠 Smart-Air AI: Predictive Electronic Nose 🌬️
An end-to-end IoT and Machine Learning system that uses a Raspberry Pi to "smell" the environment and predicts gas contamination using AI.

## 🚀 Overview
This project bridges hardware and software to create a predictive safety system. Using an MQ-135 sensor, the system streams data via MQTT to a Mac-hosted dashboard where a Random Forest model predicts the likelihood of a gas spike in real-time.

## 🛠️ Tech Stack
- **Edge Hardware:** Raspberry Pi 3, MQ-135 Gas Sensor, ADS1115 ADC, DHT11.
- **Protocol:** MQTT (Mosquitto) for real-time data bridging.
- **Machine Learning:** Scikit-Learn (Random Forest Classifier).
- **Dashboard:** Streamlit with E-Charts for advanced visualization.

## 📂 Project Structure
- `data_logger.py`: The "Edge" script running on the Raspberry Pi.
- `cleaner.py`: Data pre-processing and feature engineering (calculating voltage slope).
- `predictor_model.py`: Training script for the AI model.
- `air_quality_model.pkl`: The trained AI "Brain."
- `dashboard.py`: Interactive UI with voice alerts and AI prediction engine.

## 📊 Performance
- **Model Accuracy:** 95.45%
- **Prediction:** Real-time probability of air contamination spikes.