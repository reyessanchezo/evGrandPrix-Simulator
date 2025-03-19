#include <SoftwareSerial.h>
#include <ModbusMaster.h>

// Define software serial pins
const int RX_PIN = 10;   // Connect to RS485 module RO (Receiver Output)
const int TX_PIN = 11;   // Connect to RS485 module DI (Driver Input)
const int DE_RE_PIN = 2; // Connect to RS485 module DE and RE (Driver Enable and Receiver Enable)

// Create software serial instance
SoftwareSerial mySerial(RX_PIN, TX_PIN);

// Create ModbusMaster instance
ModbusMaster node;

// Define the RS485 control pin for transmit/receive
void preTransmission()
{
  digitalWrite(DE_RE_PIN, HIGH);
}

void postTransmission()
{
  digitalWrite(DE_RE_PIN, LOW);
}

unsigned long previousMillis = 0;
const long interval = 1000;
int regtest; // placeholder

void setup()
{
  // Initialize serial communication
  Serial.begin(19200);
  mySerial.begin(19200);

  // Initialize RS485 control pin
  pinMode(DE_RE_PIN, OUTPUT);
  digitalWrite(DE_RE_PIN, LOW);

  // Initialize Modbus communication
  node.begin(1, mySerial); // Set Modbus ID to 1
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}

void loop()
{
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval)
  {
    previousMillis = currentMillis;
    uint8_t result;
    uint16_t data[1];

    // Send a command to read a register, to device 1
    result = node.readHoldingRegisters(regtest++, 1);

    if (result == node.ku8MBSuccess)
    {
      data[0] = node.getResponseBuffer(0);
      Serial.print("Reading register ");
      Serial.print(regtest);
      Serial.print(", Register value: ");
      Serial.println(data[0]);
    }
    else
    {
      Serial.print("Error reading register: ");
      Serial.println(result);
    }
  }

  if (Serial.available())
  {
    regtest = Serial.parseInt();
    Serial.print("regtest value updated to: ");
    Serial.println(regtest);
  }
}
