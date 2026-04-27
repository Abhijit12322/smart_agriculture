#include <DHT.h>

#define DHTPIN 9
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int soilPin = A0;
const int rainPin = 8;
const int relayPin = 10;

int soilThreshold = 750;
float temperature = 0.0;
float humidity = 0.0;

void setup() {
  dht.begin();
  pinMode(rainPin, INPUT);
  pinMode(relayPin, OUTPUT);
  Serial.begin(9600);
}

int readSoilMoisture() {
  int total = 0;
  for (int i = 0; i < 5; i++) {
    total += analogRead(soilPin);
    delay(10);
  }
  return total / 5;
}

bool isRaining() {
  return digitalRead(rainPin) == LOW;
}

void loop() {
  int soilValue = readSoilMoisture();
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  bool raining = isRaining();

  if (!isnan(temp)) temperature = temp;
  if (!isnan(hum)) humidity = hum;

  bool pumpOn = (soilValue > soilThreshold) && !raining;
  digitalWrite(relayPin, pumpOn ? HIGH : LOW);

  // Serial format expected by Python backend:
  // Line 1: Soil:NNN | Rain:Yes/No | Temp:NN.NN | Hum:NN.NN
  // Line 2: Pump ON/OFF
  Serial.print("Soil:");
  Serial.print(soilValue);
  Serial.print(" | Rain:");
  Serial.print(raining ? "Yes" : "No");
  Serial.print(" | Temp:");
  Serial.print(temperature, 2);
  Serial.print(" | Hum:");
  Serial.println(humidity, 2);

  Serial.println(pumpOn ? "Pump ON" : "Pump OFF");

  delay(2000); // Match Python polling interval
}
