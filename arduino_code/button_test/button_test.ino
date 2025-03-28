const int buttonPin = D7;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT);
}

void loop() {
  Serial.println(digitalRead(buttonPin));
  delay(100);
}
