#include "TM1637.h"
#include <Encoder.h>

Encoder myEnc(D5, D6);

int oldPosition  = 0;
int minPosition = -999 * 4;
int maxPosition = 999 * 4;

// Pins definitions for TM1637 and can be changed to other ports
const int CLK = D3;
const int DIO = D4;
TM1637 tm1637(CLK, DIO);

void setup() {
    Serial.begin(9600);
    Serial.println("Encoder and 4 digit display test");
    tm1637.init();
    tm1637.set(BRIGHT_TYPICAL);//BRIGHT_TYPICAL = 2,BRIGHT_DARKEST = 0,BRIGHTEST = 7;
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
      tm1637.displayNum(float(newPosition / 4) / 100, 2, true);
      Serial.println(float(newPosition / 4) / 100);
      
    }
    delay(50);
}
