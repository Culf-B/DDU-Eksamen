#include <Wire.h>

#define SLAVE_ADDRESS 0x08

byte data[8];

void setup() 
{
  Serial.begin(9600);

  Wire.begin(SLAVE_ADDRESS);
  Wire.setClock(100000); // 400khz clock speed

  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
}

void loop() { }

void receiveData(int bytecount)
{
  
  if (Wire.available()) {
    // First byte is a 0, we dont want that
    Wire.read();
    // Second byte is length
    byte length = Wire.read();
    Serial.println(length);
    if (length == (byte)0 || length > (byte)32) {
      return;
    } else {
      data[0] = (byte)length;
    }
  }

  // Overwrite data with recieved data
  for (int i = 1; i < 8; i++) {
    if (Wire.available()) {
      data[i] = Wire.read();
    } else {
      data[i] = (byte)0;
    }
    Serial.print(data[i]);
    Serial.print(",");
  }
  Serial.println();
}

void sendData()
{
  Wire.write(data, 8);
  Serial.println("Data sent!");
}