#define CONFIG SERIAL_8N1 // a config value from HardwareSerial.h (defaults to SERIAL_8N1)

// Configuration & Pin Definitions
const int RX_PIN = 9;   // Connect to RS485 module RO (Receiver Output)
const int TX_PIN = 10;   // Connect to RS485 module DI (Driver Input)
const int DE_RE_PIN = 11; // Connect to RS485 module DE and RE (Driver/Receiver Enable)

const byte encoderPin = 13;       // Encoder output connected
const byte ledPin = LED_BUILTIN;
const byte throttlePin = 12;  //output throttle (0-5V) for a

// Timing and Constants
const float interval = 50.0; // Output interval (milliseconds)
const int pulsesPerRevolution = 60;
const float intervalPerMinute = 60000.0 / interval;

// Global Timing & States
volatile uint32_t pulseCount = 0; // Pulse counter (updated in interrupt)
unsigned long previousMillis = 0;
unsigned long currentMillis = 0;
unsigned long SerialLastRead = 0;
int actualInterval = 0;

// Dynamic Values
int rpm = 0;
String digitalTorque;
uint32_t count = 0;
uint32_t totalCount = 0;
unsigned int throttleVal = 0;

void setup() {
  Serial.begin(115200);
  Serial1.begin(19200);

  Serial.setTimeout(10);
  Serial1.setTimeout(10);

  // Set RS485 module control pin and default to receive mode
  pinMode(DE_RE_PIN, OUTPUT);
  digitalWrite(DE_RE_PIN, LOW); // LOW for receive mode

  pinMode(encoderPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  pinMode(throttlePin, OUTPUT);
  attachInterrupt(encoderPin, countPulse, RISING);
}

void loop() {
  currentMillis = millis();

  if (Serial1.available() > 0) {
    digitalTorque = Serial1.readStringUntil('\r');
  }
  if (Serial.available() > 0) {
    String temp = Serial.readStringUntil('\r');
    throttleVal = constrain((temp.toDouble()*255/3.3), 0, 255);
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
    count = pulseCount;
    currentMillis = millis();
    pulseCount = 0;
    actualInterval = currentMillis - previousMillis;
    previousMillis = currentMillis;  
    rpm = count*10; 
    /*
    pulse*(1 revolution)*(1 interval)*(1000 millis)*(60 sec)      rpm
    -------------------------------------------------------- = 10 ----
    interval*(60 pulses)*(50 millis)*(1 sec)*(1 min)              min
    */
    Serial.println(
      String(rpm) + "\t" + 
      String(totalCount) + "\t" + 
      digitalTorque + "\t" + 
      throttleVal
    );

  }
  
}

void countPulse() {
  pulseCount++;
  totalCount++;
  digitalWrite(ledPin, !digitalRead(ledPin));
}
