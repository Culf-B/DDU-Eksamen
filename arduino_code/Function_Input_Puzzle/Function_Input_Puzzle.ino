#include <ESP8266WiFi.h>
#include "TM1637.h"
#include <Encoder.h>
#include <vector>

WiFiClient client;

const char* ssid = "FP3";  // Replace with your WiFi SSID
const char* password = "kage1234";  // Replace with your WiFi password
const char* server_ip = "192.168.88.12";  // Replace with your server's IP address
const int server_port = 5000;

Encoder myEnc(D5, D6);

int oldPosition  = 0;
int minPosition = -999 * 4;
int maxPosition = 999 * 4;

// Pins definitions for TM1637 and can be changed to other ports
const int CLK = D3;
const int DIO = D4;
TM1637 tm1637(CLK, DIO);

int currentButtonState = 0;
int lastButtonState = 0;
const int buttonPin = D7;

// Result data
std::vector<int> resultData;

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(buttonPin, INPUT);

  tm1637.init();
  tm1637.set(BRIGHT_TYPICAL);//BRIGHT_TYPICAL = 2,BRIGHT_DARKEST = 0,BRIGHTEST = 7;

  // Connect to WiFi
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to the server
  if (client.connect(server_ip, server_port)) {
    Serial.println("Connected to server");
  } else {
    Serial.println("Connection to server failed");
  }
}

void loop() {
  if (client.connected()) {
    
    // Button
    currentButtonState = digitalRead(buttonPin);
    if (currentButtonState == LOW && lastButtonState == HIGH) {
      Serial.println("Button pressed!");
    }
    lastButtonState = currentButtonState;


  } else {
    // If not connected, try to reconnect
    Serial.println("Disconnected from server, trying to reconnect...");
    if (client.connect(server_ip, server_port)) {
      Serial.println("Reconnected to server");
    } else {
      Serial.println("Reconnection to server failed");
    }
  }

  delay(100);  // Small delay to avoid flooding the serial monitor
}