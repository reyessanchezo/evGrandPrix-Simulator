#include <SoftwareSerial.h>

// Define software serial pins
const int RX_PIN = 10;   // Connect to RS485 module RO (Receiver Output)
const int TX_PIN = 11;   // Connect to RS485 module DI (Driver Input)
const int DE_RE_PIN = 2; // Connect to RS485 module DE and RE (Driver/Receiver Enable)
SoftwareSerial rs485Serial(RX_PIN, TX_PIN);


// Analog measurement constants
const byte encoderPin = 3;       // Encoder output connected to digital pin 3
const byte torquePin = A4;       // Torque output connected to Analog pin 4
const int throttlePin = 6;
volatile unsigned long pulseCount = 0;
unsigned long previousMillis = 0;
const float interval = 50.0; // Output interval (milliseconds)
const float pulsesPerRevolution = 60.0;
const float intervalPerMinute = 60000.0 / interval;
const byte ledPin = 13;
float rpm = 0.0;
float analogTorque;
String digitalTorque, throttle;
int actualInterval = 0;
unsigned int count = 0;
unsigned long long currentMillis = 0;
unsigned int totalCount = 0;

void setup() {
  Serial.begin(115200);
  rs485Serial.begin(115200);

  // Set RS485 module control pin and default to receive mode
  pinMode(DE_RE_PIN, OUTPUT);
  digitalWrite(DE_RE_PIN, LOW); // LOW for receive mode

  pinMode(encoderPin, INPUT_PULLUP);
  pinMode(torquePin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(throttlePin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(encoderPin), countPulse, RISING);
}

void loop() {
  if (rs485Serial.available() > 0) {
    digitalTorque = rs485Serial.readStringUntil('\r');
    digitalTorque.trim();
  }
  if (Serial.available() > 0) {
    throttle = Serial.readStringUntil('\r');
    double throttleVal = map(throttle.toDouble(), 0, 5, 0, 255);
    analogWrite(throttlePin, throttleVal);
  }
  currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    //noInterrupts(); // Temporarily disable interrupts for accurate count
    count = pulseCount;
    currentMillis = millis();
    pulseCount = 0;
    //interrupts(); // Re-enable interrupts
    actualInterval = currentMillis - previousMillis;
    previousMillis = currentMillis;  
    
    
    // Calculate values
    analogTorque = ((analogRead(torquePin) * 60.0) / 1023.0) - 30.0;
    rpm = ((float)count * (1000.0/(float)actualInterval) * 60.0) / (float)pulsesPerRevolution;
    Serial.println(
      "RPM: " + (String)rpm + 
      " \tAnalog Torque(Nm): " + analogTorque + 
      " \tRS485 Torque(Nm): " + digitalTorque +
      " \tincoming: " + throttle +
      " \tpulses: " + (String)totalCount

    );
  }
  
}

void countPulse() {
  pulseCount++;
  totalCount++;
  digitalWrite(ledPin, !digitalRead(ledPin));
}
