#include <SoftwareSerial.h>

// Define software serial pins
const int RX_PIN = 10;   // Connect to RS485 module RO (Receiver Output)
const int TX_PIN = 11;   // Connect to RS485 module DI (Driver Input)
const int DE_RE_PIN = 2; // Connect to RS485 module DE and RE (Driver/Receiver Enable)
SoftwareSerial rs485Serial(RX_PIN, TX_PIN);


// Analog measurement constants
const byte encoderPin = 3;       // Encoder output connected to digital pin 3
const byte torquePin = A4;       // Torque output connected to Analog pin 4
const byte ledPin = 13;
const byte throttlePin = 6;

// Timing
volatile unsigned long pulseCount = 0;
unsigned long previousMillis = 0;
const float interval = 50.0; // Output interval (milliseconds)
const int pulsesPerRevolution = 60;
const float intervalPerMinute = 60000.0 / interval;

// variables
int rpm = 0;
float analogTorque;
String digitalTorque;
int actualInterval = 0;
unsigned int count = 0;
unsigned long long currentMillis = 0;
unsigned int totalCount = 0;
unsigned long SerialLastRead = 0;
double throttleVal = 0;

void setup() {
  Serial.begin(115200);
  rs485Serial.begin(19200);

  Serial.setTimeout(50);
  rs485Serial.setTimeout(10);

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
  currentMillis = millis();

  if (rs485Serial.available() > 0) {
    digitalTorque = rs485Serial.readStringUntil('\r');
  }
  if (Serial.available() > 0) {
    String temp = Serial.readStringUntil('\r');
    throttleVal = map(constrain(temp.toDouble(), 0, 5), 0, 5, 0, 255);
    analogWrite(throttlePin, throttleVal);
    SerialLastRead = millis();
  }

  // Throttle timeout
  // At the end of a simulation, stop the motor
  if ( (millis() - SerialLastRead) > 1000 ) {
    throttleVal = 0;
    analogWrite(throttlePin, throttleVal);
  }
  
  
  if (currentMillis - previousMillis >= interval) {
    noInterrupts(); // Temporarily disable interrupts for accurate count
    count = pulseCount;
    currentMillis = millis();
    pulseCount = 0;
    interrupts(); // Re-enable interrupts
    actualInterval = currentMillis - previousMillis;
    previousMillis = currentMillis;  
    rpm = (count * (1000/actualInterval) * 60) / pulsesPerRevolution;

    Serial.println(
      (String)rpm + 
      "\t" + (String)totalCount +
      "\t" + digitalTorque + "\t" + (String)SerialLastRead + "\t" + (String)throttleVal
    );
  }
  
}

void countPulse() {
  pulseCount++;
  totalCount++;
  digitalWrite(ledPin, !digitalRead(ledPin));
}
