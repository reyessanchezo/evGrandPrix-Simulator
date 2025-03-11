const byte encoderPin = 3;       // Encoder output connected to digital pin 3
const byte torquePin = A4;       // Torque output connected to Analog pin 4
volatile unsigned long pulseCount = 0;
unsigned long previousMillis = 0;
const float interval = 10.0; // Output interval (milliseconds)
const float pulsesPerRevolution = 60.0;
const float intervalPerMinute = 60000.0 / interval;
const byte ledPin = 13;
float rpm = 0.0;
float torque = 0.0;
int actualInterval = 0;
unsigned long count = 0;
unsigned long long currentMillis = 0;

void setup() {
  Serial.begin(115200);
  pinMode(encoderPin, INPUT_PULLUP);
  pinMode(torquePin, INPUT);
  pinMode(ledPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(encoderPin), countPulse, RISING);
}

void loop() {
  currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    noInterrupts(); // Temporarily disable interrupts for accurate count
    count = pulseCount;
    currentMillis = millis();
    pulseCount = 0;
    interrupts(); // Re-enable interrupts
    actualInterval = currentMillis - previousMillis;
    previousMillis = currentMillis;  
    
    
    // Calculate values
    torque = ((analogRead(torquePin) * 60.0) / 1023.0) - 30.0;
    rpm = count * (1000/actualInterval) * 60 / pulsesPerRevolution / 2;
    Serial.print("RPM: ");
    Serial.print(rpm, 1);
    Serial.print(" Torque(Nm): ");
    Serial.println(torque, 2);
  }
  
}

void countPulse() {
  pulseCount++;
  digitalWrite(ledPin, !digitalRead(ledPin));
}
