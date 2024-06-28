#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* server = "http://127.0.0.1:8000";  

const char* sensor_update_endpoint = "/sensor_update/";  
const char* usertraining_update_endpoint = "/usertraining_update/";  

const char* sensor_id = "1";
const char* user_id = "1";

WiFiClient client;
HTTPClient http;

const int ldrPin = 34;
int ldrValue;
bool pulseDetected = false;
unsigned long lastBeatTime = 0;
int beatInterval = 0;
int totalHeartRate = 0;
int numMeasurements = 0;

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
}

void loop() {
  ldrValue = analogRead(ldrPin);

  if (ldrValue < 500 && !pulseDetected) {
    pulseDetected = true;
    lastBeatTime = millis();
  }

  if (ldrValue > 700 && pulseDetected) {
    pulseDetected = false;
    beatInterval = millis() - lastBeatTime;
    int heartRate = 60000 / beatInterval;

    totalHeartRate += heartRate;
    numMeasurements++;

    int averageHeartRate = totalHeartRate / numMeasurements;

    Serial.print("Current heart rate: ");
    Serial.println(heartRate);
    Serial.print("Average heart rate: ");
    Serial.println(averageHeartRate);

    String sensor_update_url = String(server) + sensor_update_endpoint;
    http.begin(client, sensor_update_url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String sensor_update_data = "sensor_id=" + String(sensor_id) + "&pulse=" + String(heartRate);
    int sensor_update_response_code = http.POST(sensor_update_data);
    if (sensor_update_response_code > 0) {
      Serial.println("sensor_update request sent successfully");
    } else {
      Serial.print("Error sending sensor_update request: ");
      Serial.println(sensor_update_response_code);
    }
    http.end();

    String usertraining_update_url = String(server) + usertraining_update_endpoint;
    http.begin(client, usertraining_update_url);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    String usertraining_update_data = "user_id=" + String(user_id) + "&average_pulse=" + String(averageHeartRate);
    int usertraining_update_response_code = http.POST(usertraining_update_data);
    if (usertraining_update_response_code > 0) {
      Serial.println("usertraining_update request sent successfully");
    } else {
      Serial.print("Error sending usertraining_update request: ");
      Serial.println(usertraining_update_response_code);
    }
    http.end();
  }

  delay(10);
}
