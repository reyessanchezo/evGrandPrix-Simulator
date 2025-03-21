import serial
import time
from threading import Thread, Event
from queue import Queue, Empty
from multiprocessing import Process

# Reads for data from Serial.
def readingSerial(ser, event, recq):
    while not event.is_set():
        if ser.in_waiting > 0:
            try:
                received_data = ser.readline().decode('utf-8').strip()
                #print(f"{str(received_data)}")
                datfo = list(map(lambda x: x.split()[-1], received_data.split('\t')))
                #print(datfo)
                recq.put(datfo)
            except:
                pass

# Sends the voltage from the Queue to the Arduino.
def writeVoltage(serial_port: serial, sendQueue: Queue, receiveQueue: Queue):
    ser = serial.Serial(serial_port, 115200, timeout=None)

    # This is a thread to receive signals from the testing Arduino.
    stop_event = Event()
    respThread = Thread(target=readingSerial,
        args=(ser, stop_event, receiveQueue),
        daemon=True
    )
    respThread.start()

    try:
        while True:
            try:
                item = sendQueue.get()
            except Empty:
                continue
            except KeyboardInterrupt:
                stop_event.set()
                respThread.join()
                print("Closing...")
                sendQueue.task_done()
                ser.close()
                break
            else:
                if item == "EXIT":
                    stop_event.set()
                    respThread.join()
                    print("Closing...")
                    sendQueue.task_done()
                    ser.close()
                    break

                #print(f"Processing {item}")
                ser.write(bytes(str(item)+"\r", 'utf-8'))
                sendQueue.task_done()
        time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Error: {e}")

    finally:
        stop_event.set()
        ser.close()

def mywait(t):
    time.sleep(t)

if __name__ == '__main__':
    from comport_detection import *

    sendQueue = Queue()
    receiveQueue = Queue()

    sp = choose_port()

    voltageThread = Thread(
        target=writeVoltage,
        args=(sp, sendQueue, receiveQueue),
        daemon=True
    )

    voltageThread.start()

    time.sleep(3)
    """
    for i in range(100):
        sendQueue.put(i % 5)
        waitthread = Process(
            target=mywait,
            args=(0.1,)
        )
        waitthread.start()
        waitthread.join()
    """

    #queue.put("EXIT")

    i = 0
    while True:
        try:
            item = receiveQueue.get()
        except Empty:
            continue
        except KeyboardInterrupt:
            print("Ending program.")
            break
        else:
            print(f"RPM: {item[0]}\tTotal Pulses: {item[4]}\tV: {item[3]}")
            receiveQueue.task_done()
        
        #i = (i + 0.01) % 2
        sendQueue.put(2.2)

    sendQueue.put(0)
    waitthread = Process(
        target=mywait,
        args=(0.5,)
    )
    waitthread.start()
    waitthread.join()
    sendQueue.put("EXIT")
    voltageThread.join()


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