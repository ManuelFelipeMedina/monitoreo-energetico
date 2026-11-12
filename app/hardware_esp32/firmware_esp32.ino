#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Credenciales WiFi
const char* ssid = "NOMBRE_DE_TU_RED_WIFI";
const char* password = "CONTRASEÑA_WIFI";

// Reemplazar con la IP local de tu computador
const char* serverName = "http://192.168.1.15:5000/api/medicion";

const int pinADC = 34; // Pin analógico para el sensor SCT-013 + resistencia burden (280/64 ohm)

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[WiFi] Conectado exitosamente!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // Lectura analógica y conversión a corriente RMS
    int lecturaRaw = analogRead(pinADC);
    float corrienteRMS = (lecturaRaw / 4095.0) * 30.0; // Ajustar con la calibración del sensor

    StaticJsonDocument<200> doc;
    doc["corriente"] = corrienteRMS;
    String jsonOutput;
    serializeJson(doc, jsonOutput);

    int httpResponseCode = http.POST(jsonOutput);
    Serial.print("Respuesta HTTP del Servidor: ");
    Serial.println(httpResponseCode);

    http.end();
  }
  delay(2000); // Envío cada 2 segundos
}
