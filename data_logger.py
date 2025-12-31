import time
import os
import board
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json
from paho.mqtt import client as mqtt_client

# =========================
# SETTINGS
# =========================
MAC_IP = "10.122.184.52"
MQTT_TOPIC = "home/air_quality"
FILE_NAME = "smart_air_data.csv"

# Memory variables for "Forward Fill"
last_temp = 20.0
last_hum = 50.0

# =========================
# SENSOR SETUP
# =========================
dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
i2c = board.I2C()
ads = ADS.ADS1115(i2c)
mq135 = AnalogIn(ads, 0)

# =========================
# MQTT SETUP (With Reconnect Logic)
# =========================
def connect_mqtt():
    """Attempts to connect and returns the client, or None if failed."""
    try:
        # Using the newer Version 2 API as requested
        c = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
        # 5-second timeout so it doesn't hang the whole script if Mac is off
        c.connect(MAC_IP, 1883, keepalive=60)
        print("✅ MQTT Connected to Mac")
        return c
    except Exception as e:
        print(f"❌ Connection attempt failed: {e}")
        return None

client = connect_mqtt()

# CSV INIT
if not os.path.isfile(FILE_NAME):
    with open(FILE_NAME, "w") as f:
        f.write("timestamp,temperature,humidity,gas_voltage\n")

print("---- 🚀 BULLETPROOF HYBRID LOGGER STARTED ----")

# =========================
# MAIN LOOP
# =========================
try:
    while True:
        # 1. READ ANALOG GAS (Instant & Reliable)
        gas = mq135.voltage
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        # 2. TRY TO READ DHT (With Forward Fill & Retry)
        try:
            current_temp = dht.temperature
            current_hum = dht.humidity

            if current_temp is not None and current_hum is not None:
                last_temp = current_temp
                last_hum = current_hum
            else:
                # If sensor returns None, we don't crash, we just wait a second
                print("⚠️ Sensor returned None, retrying in 2s...")
                time.sleep(2)
                continue # Skip this loop iteration to try a fresh read

        except RuntimeError as e:
            # Common DHT timing error - use Forward Fill and keep moving
            print(f"⚠️ DHT Timing Glitch: {e}. Using last known: {last_temp}C")
        except Exception as e:
            print(f"❌ DHT Hardware Error: {e}")

        # 3. CONSTRUCT PAYLOAD
        payload = {
                        "timestamp": ts,
            "temperature": last_temp,
            "humidity": last_hum,
            "gas_voltage": round(gas, 4)
        }

        # 4. SAVE TO LOCAL CSV (Safety backup)
        with open(FILE_NAME, "a") as f:
            f.write(f"{ts},{last_temp},{last_hum},{gas:.3f}\n")

        # 5. SEND TO MAC (With Auto-Reconnect)
        sent_success = False
        if client:
            try:
                client.publish(MQTT_TOPIC, json.dumps(payload))
                sent_success = True
            except:
                print("📡 Connection lost. Attempting to reconnect...")
                client = connect_mqtt()
        else:
            client = connect_mqtt()

        # Status Update
        status_icon = "🚀" if sent_success else "💾 (Local Only)"
        print(f"{status_icon} SENT → T:{last_temp}°C | H:{last_hum}% | GAS:{gas:.3f}")

        # 6. WAIT FOR NEXT INTERVAL
        # Note: If we had a glitch, we already waited 2s.
        # Otherwise, wait 20s for the next standard reading.
        time.sleep(20)

 except KeyboardInterrupt:
    print("\n🛑 Stopped by user")
    if client:
        client.disconnect()