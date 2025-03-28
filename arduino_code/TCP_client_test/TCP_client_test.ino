#include <ESP8266WiFi.h>

const char* ssid = "FP3";  // Replace with your WiFi SSID
const char* password = "kage1234";  // Replace with your WiFi password
const char* server_ip = "192.168.88.12";  // Replace with your server's IP address
const int server_port = 5000;

WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(10);

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
    // Check if there is data available to read
    if (client.available()) {
      String data = client.readStringUntil('\n');
      Serial.print("Received from server: ");
      Serial.println(data);
    }

    // Send data to the server
    if (Serial.available()) {
      String message = Serial.readStringUntil('\n');
      client.println(message);
      Serial.print("Sent to server: ");
      Serial.println(message);
    }
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
