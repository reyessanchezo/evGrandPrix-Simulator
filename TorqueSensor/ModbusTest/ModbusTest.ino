#include <SoftwareSerial.h>

// Define software serial pins
const int RX_PIN = 10;   // Connect to RS485 module RO (Receiver Output)
const int TX_PIN = 11;   // Connect to RS485 module DI (Driver Input)
const int DE_RE_PIN = 2; // Connect to RS485 module DE and RE (Driver/Receiver Enable), 

// Create software serial instance for RS485 communication
SoftwareSerial rs485Serial(RX_PIN, TX_PIN);

void setup() {
  // Initialize hardware serial for debugging/monitor display
  Serial.begin(115200);

  // Initialize the RS485 serial communication
  rs485Serial.begin(19200);

  // Set RS485 module control pin and default to receive mode
  pinMode(DE_RE_PIN, OUTPUT);
  digitalWrite(DE_RE_PIN, LOW); // LOW for receive mode
}

void loop() {
  
  if (rs485Serial.available() > 50) {
    String message = rs485Serial.readStringUntil('\r');
    message.trim();
    Serial.println("Received Message: " + message);
  }
  
}

