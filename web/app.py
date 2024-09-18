from flask import Flask, request, render_template, jsonify
import threading
import time
import requests
from datetime import datetime

app = Flask(__name__)

# Variabili globali
sites = []
request_method = 'POST'
interval = 60
continue_sending = False
last_message = "Nessun messaggio ricevuto"
last_timestamp = None
send_statuses = []

# Pagina principale
@app.route('/', methods=['GET', 'POST'])
def index():
    global sites, request_method, interval, continue_sending

    if request.method == 'POST':
        sites_input = request.form.get('sites')
        request_method = request.form.get('method')
        interval = int(request.form.get('interval'))

        # Elabora i siti dalla textbox
        sites = [site.strip() for site in sites_input.splitlines() if site.strip()]
        continue_sending = True

    return render_template('index.html')

# Endpoint per ricevere lo stato corrente
@app.route('/status', methods=['GET'])
def status():
    readable_timestamp = last_timestamp.strftime('%Y-%m-%d %H:%M:%S') if last_timestamp else "Nessun timestamp ricevuto"
    return jsonify({
        'last_message': last_message,
        'readable_timestamp': readable_timestamp,
        'send_statuses': send_statuses
    })

# Ricezione dati dall'ESP32
@app.route('/receive_data', methods=['POST'])
def receive_data():
    global last_message, last_timestamp
    data = request.json
    last_message = str(data)  # Salva il messaggio ricevuto

    # Estrai e converti il timestamp
    if "timestamp" in data:
        last_timestamp = datetime.fromtimestamp(int(data["timestamp"]))

    if continue_sending:
        threading.Thread(target=send_data_to_sites, args=(data,)).start()
    return "Data received"

# Funzione per inviare i dati ai siti
def send_data_to_sites(data):
    global continue_sending, send_statuses

    send_statuses.clear()  # Resetta lo stato di invio per ogni nuova sessione

    while continue_sending:
        for site in sites:
            try:
                if request_method == 'POST':
                    response = requests.post(site, json=data)
                else:
                    response = requests.get(site, params=data)

                status_message = f"Sent data to {site}: {response.status_code}"
                send_statuses.append(status_message)
            except Exception as e:
                status_message = f"Error sending data to {site}: {e}"
                send_statuses.append(status_message)
        
        time.sleep(interval)

# Pagina per interrompere l'invio
@app.route('/stop', methods=['POST'])
def stop_sending():
    global continue_sending
    continue_sending = False
    return "Sending stopped"

# Avvio dell'app Flask
if __name__ == '__main__':
    app.run(debug=True)
