import time
import os
import board
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import json
from paho.mqtt import client as mqtt_client


MAC_IP = "10.122.184.52"
MQTT_TOPIC = "home/air_quality"
FILE_NAME = "smart_air_data.csv"


last_temp = 20.0
last_hum = 50.0


dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
i2c = board.I2C()
ads = ADS.ADS1115(i2c)
mq135 = AnalogIn(ads, 0)


def connect_mqtt():
    """Attempts to connect and returns the client, or None if failed."""
    try:
        
        c = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
       
        c.connect(MAC_IP, 1883, keepalive=60)
        print("✅ MQTT Connected to Mac")
        return c
    except Exception as e:
        print(f"❌ Connection attempt failed: {e}")
        return None

client = connect_mqtt()


if not os.path.isfile(FILE_NAME):
    with open(FILE_NAME, "w") as f:
        f.write("timestamp,temperature,humidity,gas_voltage\n")

print("---- 🚀 BULLETPROOF HYBRID LOGGER STARTED ----")


try:
    while True:
      
        gas = mq135.voltage
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

      
        try:
            current_temp = dht.temperature
            current_hum = dht.humidity

            if current_temp is not None and current_hum is not None:
                last_temp = current_temp
                last_hum = current_hum
            else:
                
                print("⚠️ Sensor returned None, retrying in 2s...")
                time.sleep(2)
                continue 

        except RuntimeError as e:
           
            print(f"⚠️ DHT Timing Glitch: {e}. Using last known: {last_temp}C")
        except Exception as e:
            print(f"❌ DHT Hardware Error: {e}")

        
        payload = {
                        "timestamp": ts,
            "temperature": last_temp,
            "humidity": last_hum,
            "gas_voltage": round(gas, 4)
        }

      
        with open(FILE_NAME, "a") as f:
            f.write(f"{ts},{last_temp},{last_hum},{gas:.3f}\n")

        
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

        
        status_icon = "🚀" if sent_success else "💾 (Local Only)"
        print(f"{status_icon} SENT → T:{last_temp}°C | H:{last_hum}% | GAS:{gas:.3f}")

        
        time.sleep(20)

 except KeyboardInterrupt:
    print("\n🛑 Stopped by user")
    if client:
        client.disconnect()
