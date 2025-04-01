#include <ESP8266WiFi.h>
#include "TM1637.h"
#include <Encoder.h>
#include <vector>

#include "secrets.h"

WiFiClient client;

const char* ssid = SECRET_SSID;  // Replace with your WiFi SSID
const char* password = SECRET_PASSWORD;  // Replace with your WiFi password
const char* server_ip = "10.42.0.1";  // Replace with your server's IP address
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

bool started = false;
bool indexChosen = false;

// Info to send
const int controllerID = 0; // Identify this device
// Input values
int indexToSend = 0;
float valueToSend = 0.0;
String stringToSend = "";

// Encoder readings
int latestEncoderInt = 0;
float latestEncoderFloat = 0.0;

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

  tm1637.displayNum(4001, 0, false);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  tm1637.displayNum(4002, 0, false);

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to the server
  if (client.connect(server_ip, server_port)) {
    Serial.println("Connected to server");
    tm1637.displayNum(0, 0, false);
  } else {
    Serial.println("Connection to server failed");
  }
}

void loop() {
  int newPosition = myEnc.read();

  if (newPosition > maxPosition) {
    myEnc.write(minPosition);
    newPosition = minPosition;
  } else if (newPosition < minPosition) {
    myEnc.write(maxPosition);
    newPosition = maxPosition;
  }

  if (newPosition != oldPosition) {
    oldPosition = newPosition;

    latestEncoderInt = newPosition / 4;
    latestEncoderFloat = float(newPosition / 4) / 100;
  }

  if (client.connected()) {
    
    // Button
    currentButtonState = digitalRead(buttonPin);
    if (currentButtonState == LOW && lastButtonState == HIGH) {
      if (started == false) {
        started = true;
        myEnc.write(0);
      } else {
        if (indexChosen == true) {
          valueToSend = latestEncoderFloat;
          send();
          started = false;
          myEnc.write(0);
        } else {
          indexChosen = true;
          indexToSend = latestEncoderInt;
          if (indexToSend < 0) {
            indexToSend = indexToSend * -1;
          }
          myEnc.write(0);
        }
      }
    }
    lastButtonState = currentButtonState;

    if (started == false) {
      // Display waiting screen
      tm1637.displayNum(random(9999), 0);
    } else if (indexChosen == false) {
      // Choose index
      tm1637.displayNum(latestEncoderInt, 0, false);
    } else {
      // Choose value
      tm1637.displayNum(latestEncoderFloat, 2, true);
    }


  } else {
    // If not connected, try to reconnect
    tm1637.displayNum(4002, 0, false);

    Serial.println("Disconnected from server, trying to reconnect...");
    if (client.connect(server_ip, server_port)) {
      Serial.println("Reconnected to server");
    } else {
      Serial.println("Reconnection to server failed");
    }
  }

  delay(100);  // Small delay to avoid flooding the serial monitor
}

void send() {
  stringToSend = "";
  stringToSend = stringToSend + controllerID;
  stringToSend = stringToSend + ",";
  stringToSend = stringToSend + indexToSend;
  stringToSend = stringToSend + ",";
  stringToSend = stringToSend + valueToSend;

  client.println(stringToSend);

  indexChosen = false;
  indexToSend = 0;
  valueToSend = 0.0;
}