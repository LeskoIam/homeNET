#include "DHT.h"
#include <OneWire.h>
#include <DallasTemperature.h>

int DS18B20_pin = 3;
OneWire  oneWire(DS18B20_pin);
DallasTemperature sensors(&oneWire);

int DHT22_pin = 4;
// Initialize DHT sensor for normal 16mhz Arduino
DHT dht(DHT22_pin, DHT22);

int LDR_pin = 5;

int active_led_pin = 13;

int command;

void setup() {
  Serial.begin(115200);
  dht.begin();
  sensors.begin();
  pinMode(active_led_pin, OUTPUT);
  Serial.println("Setup done!");
  Serial.print("\n>> ");
}

void loop() 
{
  // readingSensorsBlink();
  handleSerialCom();
}

// #########################################

void handleSerialCom()
{
  if (Serial.available() > 0)
  {
    command = Serial.parseInt();
//    m_num = Serial.parseInt();
//    par = Serial.parseInt();
//    Serial.print(command);
//    Serial.print(" ");
//    Serial.print(m_num);
//    Serial.print(" ");
//    Serial.println(par);
    
    switch (command)
    {
      // Get DS15B20 temperature
      case 1:
        readingSensorsBlink();
        Serial.print("DS18B20 temperature ");
        Serial.println(get_ds18b20_temperature());
        Serial.println("OK");
        break;
      // Get DHT22 temperature
      case 2:
        readingSensorsBlink();
        Serial.print("DHT22 temperature ");
        Serial.println(get_DHT22_temperature());
        Serial.println("OK");
        break;
      // Get DHT22 humidity
      case 3:
        readingSensorsBlink();
        Serial.print("DHT22 humidity ");
        Serial.println(get_DHT22_humidity());
        Serial.println("OK");
        break;
      // Get LDR ligh level
      case 4:
        readingSensorsBlink();
        Serial.print("LDR light level ");
        Serial.println(analogRead(LDR_pin));
        Serial.println("OK");
        break;
      default:
        Serial.println("NOK");
        break;
    }
    Serial.print(">> ");
  }
}

float get_ds18b20_temperature()
{
  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);
  return temp;
    
}

float get_DHT22_temperature()
{
  float temp = dht.readTemperature();
  return temp;
    
}

float get_DHT22_humidity()
{
  float hum = dht.readHumidity();
  return hum;
}

int get_LDR()
{
  int light = analogRead(LDR_pin);
  return light;
}

// #########################################

void readingSensorsBlink()
{
  digitalWrite(active_led_pin, HIGH);
  delay(20);
  digitalWrite(active_led_pin, LOW);
  delay(10);
}

