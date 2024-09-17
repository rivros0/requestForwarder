import requests
import random
import time
from datetime import datetime, timezone, timedelta

# Configurazione Flask
server_url = "http://your-flask-app.pythonanywhere.com/receive_data"

# Funzione per simulare i dati dei sensori
def get_sensor_data():
    distance = round(random.uniform(10.0, 100.0), 2)  # Simula distanza in cm
    temperature = round(random.uniform(20.0, 30.0), 2)  # Simula temperatura in gradi Celsius
    humidity = round(random.uniform(30.0, 70.0), 2)  # Simula umidità in %
    light_level = random.randint(0, 1023)  # Simula livello di luce (ADC 0-1023)
    
    return {
        "distance": distance,
        "temperature": temperature,
        "humidity": humidity,
        "light": light_level
    }

# Funzione per ottenere il timestamp corrente in GMT+1
def get_timestamp():
    gmt_offset = timedelta(hours=1)
    current_time = datetime.now(timezone.utc) + gmt_offset
    timestamp = int(current_time.timestamp())
    return timestamp

# Funzione per inviare i dati al server Flask
def send_data():
    sensor_data = get_sensor_data()
    timestamp = get_timestamp()
    
    # Creazione del payload JSON
    payload = {
        "distance": sensor_data["distance"],
        "temperature": sensor_data["temperature"],
        "humidity": sensor_data["humidity"],
        "light": sensor_data["light"],
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(server_url, json=payload)
        if response.status_code == 200:
            print(f"Data sent successfully: {response.text}")
        else:
            print(f"Failed to send data. HTTP Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Loop principale
if __name__ == "__main__":
    while True:
        send_data()
        time.sleep(60)  # Invia i dati ogni 60 secondi
