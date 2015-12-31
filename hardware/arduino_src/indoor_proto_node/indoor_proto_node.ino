#include "DHT.h"
#include <OneWire.h>
#include <DallasTemperature.h>

int NODE_ID = 1;

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
  Serial.setTimeout(10);  // fine tune it with o-scope!
  dht.begin();
  sensors.begin();
  pinMode(active_led_pin, OUTPUT);
  Serial.print("Node: ");
  Serial.print(NODE_ID);
  Serial.println("... setup done!");
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
        led_on();
        Serial.print("DS18B20 temperature ");
        Serial.println(get_ds18b20_temperature());
        Serial.println("OK");
        break;
      // Get DHT22 temperature
      case 2:
        led_on();
        Serial.print("DHT22 temperature ");
        Serial.println(get_DHT22_temperature());
        Serial.println("OK");
        break;
      // Get DHT22 humidity
      case 3:
        led_on();
        Serial.print("DHT22 humidity ");
        Serial.println(get_DHT22_humidity());
        Serial.println("OK");
        break;
      // Get LDR ligh level
      case 4:
        led_on();
        Serial.print("LDR light level ");
        Serial.println(analogRead(LDR_pin));
        Serial.println("OK");
        break;
      case 9:
        led_on();
        Serial.print("Node ID ");
        Serial.println(get_node_id());
        Serial.println("OK");
        break;
      default:
        Serial.println("NOK");
        break;
    }
    led_off();
    Serial.print(">> ");
  }
}

float get_ds18b20_temperature()
{
  sensors.requestTemperatures();
  delay(10);
  sensors.getTempCByIndex(0);
  sensors.requestTemperatures();
  delay(10);
  float temp = sensors.getTempCByIndex(0);
  return temp;
    
}

float get_DHT22_temperature()
{
  dht.readTemperature();
  delay(10);
  float temp = dht.readTemperature();
  return temp;
    
}

float get_DHT22_humidity()
{
  dht.readHumidity();
  delay(10);
  float hum = dht.readHumidity();
  return hum;
}

int get_LDR()
{
  analogRead(LDR_pin);
  delay(10);
  int light = analogRead(LDR_pin);
  return light;
}

int get_node_id()
{
  return NODE_ID;
}
  

// #########################################

void led_on()
{
  digitalWrite(active_led_pin, HIGH);
}

void led_off()
{
  digitalWrite(active_led_pin, LOW);
}

