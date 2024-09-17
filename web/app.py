from flask import Flask, request, render_template
import threading
import time
import requests

app = Flask(__name__)

# Variabili globali per memorizzare i siti, metodo e intervallo
sites = []
request_method = 'POST'
interval = 60
continue_sending = False

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

    return render_template('index.html', sites=sites, method=request_method, interval=interval)

# Ricezione dati dall'ESP32
@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    if continue_sending:
        threading.Thread(target=send_data_to_sites, args=(data,)).start()
    return "Data received"

# Funzione per inviare i dati ai siti
def send_data_to_sites(data):
    global continue_sending

    while continue_sending:
        for site in sites:
            try:
                if request_method == 'POST':
                    response = requests.post(site, json=data)
                else:
                    response = requests.get(site, params=data)

                print(f"Sent data to {site}: {response.status_code}")
            except Exception as e:
                print(f"Error sending data to {site}: {e}")
        
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
