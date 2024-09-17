#include <WiFi.h>
#include <HTTPClient.h>
#include <Ultrasonic.h>
#include <DHT.h>
#include <time.h>

// Configurazione WiFi
const char* ssid = "Your_SSID";       // Inserisci il nome della rete WiFi
const char* password = "Your_PASSWORD"; // Inserisci la password della rete WiFi

// Configurazione Flask
const char* serverName = "http://your-flask-app.pythonanywhere.com/receive_data";

// Configurazione sensori
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

Ultrasonic ultrasonic(5, 18);
const int lightSensorPin = 34;

// Configurazione NTP
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600; // Offset per GMT+1
const int daylightOffset_sec = 0; // Nessun offset per l'ora legale

void setup() {
  Serial.begin(115200);
  pinMode(lightSensorPin, INPUT);

  // Avvio del sensore DHT
  dht.begin();

  // Connessione al WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  // Configura l'ora NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Creazione URL di destinazione
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // Acquisizione dati dai sensori
    float distance = ultrasonic.read();
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int lightLevel = analogRead(lightSensorPin);

    // Ottieni il timestamp attuale
    time_t now;
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
      Serial.println("Failed to obtain time");
      return;
    }
    time(&now);
    String timestamp = String(now);

    // Creazione payload JSON
    String jsonPayload = "{";
    jsonPayload += "\"distance\":" + String(distance) + ",";
    jsonPayload += "\"temperature\":" + String(temperature) + ",";
    jsonPayload += "\"humidity\":" + String(humidity) + ",";
    jsonPayload += "\"light\":" + String(lightLevel) + ",";
    jsonPayload += "\"timestamp\":\"" + timestamp + "\"";
    jsonPayload += "}";

    // Invia richiesta POST
    int httpResponseCode = http.POST(jsonPayload);

    // Gestione della risposta
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }

    // Chiusura connessione
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  // Attendere prima di inviare nuovamente
  delay(60000); // 60 secondi
}
