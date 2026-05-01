#define BLYNK_TEMPLATE_ID ""
#define BLYNK_TEMPLATE_NAME ""
#define BLYNK_AUTH_TOKEN ""

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

// ---------------- WIFI ----------------
char ssid[] = "";
char pass[] = "";

// ---------------- FLASK SERVER ----------------
const char* serverName = "http://YOUR_IPV4_ADDRESS:5000//predict";

// ---------------- PINS ----------------
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_PIN 34
#define RELAY_PIN 25

DHT dht(DHTPIN, DHTTYPE);

// ---------------- VARIABLES ----------------
int cropType = 0;
int growthStage = 0;

bool autoMode = false;
bool pumpRunning = false;

unsigned long pumpStartTime = 0;
unsigned long pumpDuration = 0;

bool lastPumpState = false;
bool lastModeState = false;

// ---------------- BLYNK INPUT ----------------
BLYNK_WRITE(V4) { cropType = param.asInt(); }
BLYNK_WRITE(V5) { growthStage = param.asInt(); }

// ---------------- MODE SWITCH (V6) ----------------
BLYNK_WRITE(V6)
{
  autoMode = param.asInt();

  if (autoMode != lastModeState)
  {
    lastModeState = autoMode;

    if (autoMode)
    {
      Serial.println(">>> AUTO MODE ENABLED");
      Blynk.logEvent("mode_auto", "System switched to AUTO mode");
    }
    else
    {
      Serial.println(">>> MANUAL MODE ENABLED");
      Blynk.logEvent("mode_manual", "System switched to MANUAL mode");
    }
  }
}

// ---------------- MANUAL PUMP (V3) ----------------
BLYNK_WRITE(V3)
{
  int state = param.asInt();

  if (!autoMode)
  {
    if (state == 1)
    {
      digitalWrite(RELAY_PIN, LOW);
      pumpRunning = true;
      pumpStartTime = millis();

      if (!lastPumpState)
      {
        lastPumpState = true;
        Blynk.logEvent("pump_on", "Pump turned ON manually");
      }

      Serial.println(">>> PUMP ON (MANUAL)");
    }
    else
    {
      digitalWrite(RELAY_PIN, HIGH);
      pumpRunning = false;

      if (lastPumpState)
      {
        lastPumpState = false;
        Blynk.logEvent("pump_off", "Pump turned OFF manually");
      }

      Serial.println(">>> PUMP OFF (MANUAL)");
    }
  }
}

// ---------------- SETUP ----------------
void setup()
{
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  dht.begin();

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  Serial.println("================================");
  Serial.println("SMART IRRIGATION SYSTEM STARTED");
  Serial.println("================================");
}

// ---------------- LOOP ----------------
void loop()
{
  Blynk.run();

  // ---------------- AUTO STOP PUMP ----------------
  if (pumpRunning && pumpDuration > 0 &&
      millis() - pumpStartTime >= pumpDuration)
  {
    digitalWrite(RELAY_PIN, HIGH);
    pumpRunning = false;

    if (lastPumpState)
    {
      lastPumpState = false;
      Blynk.logEvent("pump_off", "Pump stopped after timeout");
    }

    Serial.println(">>> PUMP OFF (TIMEOUT)");
  }

  // ---------------- SENSOR READ ----------------
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int soilRaw = analogRead(SOIL_PIN);

  if (isnan(temp) || isnan(hum))
  {
    Serial.println("!!! DHT ERROR");
    delay(2000);
    return;
  }

  int soil = map(soilRaw, 4095, 1500, 0, 100);
  soil = constrain(soil, 0, 100);

  String cropName = (cropType == 0) ? "Chilli" : "Carrot";
  String stages[] = {"Germination", "Vegetative", "Flowering", "Fruiting"};
  String stageName = stages[growthStage];

  // ---------------- SERIAL DEBUG (IMPORTANT FIX) ----------------
  Serial.println("\n------ SENSOR DATA ------");
  Serial.print("Soil: "); Serial.println(soil);
  Serial.print("Temp: "); Serial.println(temp);
  Serial.print("Humidity: "); Serial.println(hum);
  Serial.print("Crop: "); Serial.println(cropName);
  Serial.print("Stage: "); Serial.println(stageName);

  // ---------------- SEND TO BLYNK ----------------
  Blynk.virtualWrite(V0, soil);
  Blynk.virtualWrite(V1, temp);
  Blynk.virtualWrite(V2, hum);

  // ---------------- AUTO MODE (FLASK + ML) ----------------
  if (autoMode && WiFi.status() == WL_CONNECTED)
  {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"soil\":" + String(soil) + ",";
    json += "\"temp\":" + String(temp) + ",";
    json += "\"humidity\":" + String(hum) + ",";
    json += "\"crop\":\"" + cropName + "\",";
    json += "\"stage\":\"" + stageName + "\"";
    json += "}";

    Serial.println("Sending to Flask:");
    Serial.println(json);

    int httpResponseCode = http.POST(json);

    Serial.print("HTTP Response: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0)
    {
      String response = http.getString();
      Serial.println("Response:");
      Serial.println(response);

      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, response);

      if (error)
      {
        Serial.print("JSON ERROR: ");
        Serial.println(error.c_str());
        return;
      }

      int water = doc["water"];
      int duration = doc["duration"];

      pumpDuration = duration * 1000;

      if (water == 1)
      {
        digitalWrite(RELAY_PIN, LOW);
        pumpRunning = true;
        pumpStartTime = millis();

        if (!lastPumpState)
        {
          lastPumpState = true;
          Blynk.logEvent("pump_on", "Pump turned ON (AUTO)");
        }

        Serial.println(">>> PUMP ON (AUTO)");
      }
      else
      {
        digitalWrite(RELAY_PIN, HIGH);
        pumpRunning = false;

        if (lastPumpState)
        {
          lastPumpState = false;
          Blynk.logEvent("pump_off", "Pump turned OFF (AUTO)");
        }

        Serial.println(">>> NO WATERING REQUIRED");
      }
    }

    http.end();
  }

  delay(5000);
}
