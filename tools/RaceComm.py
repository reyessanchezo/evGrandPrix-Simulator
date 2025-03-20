import serial
import time
from threading import Thread, Event
from queue import Queue, Empty

# Reads for data from Serial.
def readingSerial(ser, event):
    while not event.is_set():
        if ser.in_waiting > 0:
            received_data = ser.read(4).decode('utf-8').strip()
            print(f"Arduino says: {str(received_data)}")

# Sends the voltage from the Queue to the Arduino.
def writeVoltage(serial_port: serial, queue: Queue):
    ser = serial.Serial(serial_port, 115200, timeout=0)

    # This is a thread to receive signals from the testing Arduino.
    stop_event = Event()
    respThread = Thread(target=readingSerial,
        args=(ser, stop_event),
        daemon=True
    )
    respThread.start()

    try:
        while True:
            try:
                item = queue.get()
            except Empty:
                continue
            else:
                if item == "EXIT":
                    stop_event.set()
                    respThread.join()
                    print("Closing...")
                    queue.task_done()
                    ser.close()
                    break
                
                print(f"Processing {item}")
                ser.write(bytes(str(item)+"\r", 'utf-8'))
                queue.task_done()
                time.sleep(0.5)

    except KeyboardInterrupt as e:
        print(f"Enter program.")

    except serial.SerialException as e:
        print(f"Error: {e}")

    finally:
        stop_event.set()
        ser.close()

if __name__ == '__main__':
    from comport_detection import *

    queue = Queue()

    sp = choose_port()

    voltageThread = Thread(
        target=writeVoltage,
        args=(sp, queue),
        daemon=True
    )

    voltageThread.start()

    for i in range(10):
        print(i + 2)
        queue.put(i + 2)
        time.sleep(1)

    queue.put("EXIT")
    queue.join()
    time.sleep(2)


# Arduino Code
"""
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop() {
  char x = '0';
  if (Serial.available() > 0){
    x = Serial.read();
    Serial.print(x);
    delay(10);
  }
}
"""