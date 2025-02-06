
#include <SoftwareSerial.h>

const int SSERIAL_RX_PIN = 10;  //Soft Serial Receive pin
const int SSERIAL_TX_PIN = 11;  //Soft Serial Transmit pin
const int SSERIAL_CTRL_PIN = 3;   //RS485 Direction control
const int LED_PIN = 13;
const int RS485_TRANSMIT = HIGH;
const int RS485_RECEIVE = LOW;
const unsigned char SensorRead = 0x03;
const long interval = 1000;

// Create Soft Serial Port object and define pins to use
SoftwareSerial RS485Serial(SSERIAL_RX_PIN, SSERIAL_TX_PIN);

int byteReceived;
int byteSent;
unsigned long previousMillis = 0;
unsigned long currentMillis = millis();
//===============================================================================
//  Initialization
//===============================================================================
void setup() 
{
  Serial.begin(19200);         // Start the built-in hardware serial port
  Serial.println("Receiver");  
  
  pinMode(LED_PIN, OUTPUT);   // Configure any output pins
  pinMode(SSERIAL_CTRL_PIN, OUTPUT);  
  
  digitalWrite(SSERIAL_CTRL_PIN, RS485_RECEIVE);  // Put RS485 in receive mode
  
  RS485Serial.begin(19200);   // Start the RS485 soft serial port 
}
//===============================================================================
//  Main
//===============================================================================
void loop() 
{
  currentMillis = millis();
  
  // Check if it's time to send the ping
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; // Save the last time a ping was sent
    
    // Send the ping
    digitalWrite(SSERIAL_CTRL_PIN, RS485_TRANSMIT);  // Put RS485 in Transmit mode    
    Serial.print("Sending: ");  
    Serial.println(SensorRead);
    RS485Serial.write(SensorRead);                     // Send the byte back to Master
    delay(1);                                        // Wait before going back to Receive mode
    digitalWrite(SSERIAL_CTRL_PIN, RS485_RECEIVE);   // Put RS485 back into Receive mode
  }
  
  if (RS485Serial.available())        // If data has come in from Master
  {
    byteSent = RS485Serial.read();    // Read the byte 
    Serial.write(byteSent);           // Show on local Serial Monitor window
    digitalWrite(LED_PIN, HIGH);      // Show activity on LED
    delay(10);              

    digitalWrite(SSERIAL_CTRL_PIN, RS485_RECEIVE);   // Put RS485 back into Receive mode 
    digitalWrite(LED_PIN, LOW);                      // Turn LED back off
  }  
}
