import streamlit as st
import pandas as pd
import paho.mqtt.client as mqtt
import json
import os
import subprocess
import joblib
from streamlit_echarts import st_echarts  # ADDED: For the speedometer

# --- CONFIG ---
MQTT_TOPIC = "home/air_quality"
MAC_DATA_FILE = "mac_sensor_data.csv"
MODEL_FILE = "air_quality_model.pkl"

# --- HELPERS ---
def voltage_to_aqi(voltage):
    # Mapping 0.2V (Clean) to 3.0V (Danger) into a 0-500 AQI scale
    aqi = ((voltage - 0.2) / (3.0 - 0.2)) * 500
    return int(max(0, min(500, aqi)))

# --- LOAD AI BRAIN ---
try:
    model = joblib.load(MODEL_FILE)
    model_loaded = True
except:
    model_loaded = False

# --- DATA HANDLING ---
if not os.path.exists(MAC_DATA_FILE):
    df = pd.DataFrame(columns=["timestamp", "temperature", "humidity", "gas_voltage"])
    df.to_csv(MAC_DATA_FILE, index=False)

if 'last_status' not in st.session_state:
    st.session_state.last_status = "CLEAN"

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        new_data = pd.DataFrame([payload])
        new_data.to_csv(MAC_DATA_FILE, mode='a', header=False, index=False)
    except:
        pass

@st.cache_resource
def init_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    return client

client = init_mqtt()

# --- UI SETUP ---
st.set_page_config(page_title="AI Air Monitor", layout="wide")
st.title("🧠 Smart Air Quality Analytics (AI Enabled)")

try:
    if os.path.exists(MAC_DATA_FILE):
        data = pd.read_csv(MAC_DATA_FILE)
        if len(data) > 1:
            last_row = data.iloc[-1]
            prev_row = data.iloc[-2]
            gas_val = last_row['gas_voltage']
            aqi_val = voltage_to_aqi(gas_val)
            vol_change = gas_val - prev_row['gas_voltage']

            # 1. VISUAL METRICS (Thermometer & Humidity Drops)
            col_t, col_h = st.columns(2)
            
            with col_t:
                st.subheader("🌡️ Thermometer")
                temp = last_row['temperature']
                st.write(f"### {temp} °C")
                # Custom progress bar acting as a vertical-ish thermometer
                st.progress(min(temp / 50.0, 1.0)) 
                
            with col_h:
                st.subheader("💧 Humidity")
                hum = last_row['humidity']
                # Dynamic water drops based on humidity
                drops = "💧" * int(hum / 20)
                st.write(f"### {hum} % {drops}")
                st.write("Moisture level in air")

            st.divider()

            # 2. AQI SPEEDOMETER
            st.subheader("📟 Air Quality Index (AQI) Speedometer")
            gauge_options = {
                "series": [{
                    "type": "gauge",
                    "startAngle": 180,
                    "endAngle": 0,
                    "min": 0,
                    "max": 500,
                    "itemStyle": {"color": "#FFAB00"},
                    "progress": {"show": True, "width": 18},
                    "pointer": {"show": True},
                    "axisLine": {"lineStyle": {"width": 18}},
                    "axisTick": {"show": False},
                    "splitLine": {"show": False},
                    "axisLabel": {"show": False},
                    "anchor": {"show": True, "showAbove": True, "size": 25, "itemStyle": {"borderWidth": 10}},
                    "title": {"show": False},
                    "detail": {
                        "valueAnimation": True,
                        "fontSize": 40,
                        "offsetCenter": [0, "70%"],
                        "formatter": "{value} AQI",
                        "color": "inherit"
                    },
                    "data": [{"value": aqi_val}]
                }]
            }
            st_echarts(options=gauge_options, height="400px")

            # 3. AI PREDICTION ENGINE
            st.divider()
            st.subheader("🤖 AI Prediction Engine")
            
            if model_loaded:
                prediction_prob = model.predict_proba([[gas_val, vol_change]])[0][1]
                prob_percent = round(prediction_prob * 100, 2)
                
                st.write(f"**Spike Probability:** {prob_percent}%")
                # Visualizing prediction as a mini graph-bar
                st.progress(prediction_prob)
                
                if prediction_prob > 0.8:
                    st.error("🚨 AI WARNING: High probability of air contamination!")
                elif prediction_prob > 0.4:
                    st.warning("⚠️ AI NOTICE: Detecting unusual gas movement.")
                else:
                    st.success("✅ AI STATUS: Air patterns are normal.")

            # 4. VOICE & LOGS
            if gas_val > 0.75 and st.session_state.last_status != "DANGER":
                subprocess.Popen(["say", "Warning! High gas levels detected."])
                st.session_state.last_status = "DANGER"
            elif gas_val < 0.45:
                st.session_state.last_status = "CLEAN"

            st.divider()
            st.subheader("📈 Gas Trend & Real-time Logs")
            st.line_chart(data.set_index('timestamp')['gas_voltage'])
            st.dataframe(data.tail(5), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")

if st.sidebar.button('🔄 Refresh'):
    st.rerun()
