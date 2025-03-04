const byte encoderPin = 2;       // Encoder output connected to digital pin 2
volatile unsigned long pulseCount = 0;
unsigned long previousMillis = 0;
const unsigned long interval = 1000; // Interval for RPM calculation (1 second)
const unsigned int pulsesPerRevolution = 60;
const byte ledPin = 13;

void setup() {
  Serial.begin(9600);
  pinMode(encoderPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(encoderPin), countPulse, RISING);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    noInterrupts(); // Temporarily disable interrupts for accurate count
    unsigned long count = pulseCount;
    pulseCount = 0;
    interrupts(); // Re-enable interrupts
    previousMillis = currentMillis;
    
    // Calculate RPM
    float rpm = count / pulsesPerRevolution;
    Serial.print("RPM: ");
    Serial.println(rpm);
  }
}

void countPulse() {
  pulseCount++;
  digitalWrite(ledPin, !digitalRead(ledPin));
}
