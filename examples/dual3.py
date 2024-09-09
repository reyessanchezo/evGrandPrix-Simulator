import pyvesc
from pyvesc import GetFirmwareVersion, GetValues, SetRPM, SetCurrent, SetRotorPositionMode, GetRotorPosition, SetDutyCycle, SetPosition, GetRotorPositionCumulative, SetCurrentGetPosCumulative, SetPositionCumulative, SetTerminalCommand, GetPrint, GetConfig, SetConfig, SetAlive, GetDetectEncoder
import serial
import os,sys
import math
import time
#import matplotlib.pyplot as plt
#import numpy as np
import struct
#from xml.dom import minidom

# Set your serial port here (either /dev/ttyX or COMX)
serialport = '/dev/cu.usbmodem3011'

serialArduino = '/dev/tty.usbmodem14101'
ard_length = 4 # Number of values expected from arduino

fname = ''
f = None
if len(sys.argv) > 1:
  fname = sys.argv[1]
  f = open(fname, 'w')

labels = ['Millis', 
          'RPM', 
          #'Force Count', 
          'FtLb', 
          'HP', 
          'Watt', 
          'Fet Temp F', 
          'Motor Temp F', 
          'In Volt',
          'Motor current A', 
          'Input current A',
          'Duty']

print("port " + serialport)
    
def ctof(value):
  return (value * 9.0/5) + 32

def get_values_example():    
    inbuf = b''    
    inard = b''
    
    with serial.Serial(serialport, baudrate=115200, timeout=0) as ser:
      with serial.Serial(serialArduino, baudrate=115200, timeout=0) as ard:
        try:
            ser.flushInput()
            ser.flushOutput()

            ser.write(pyvesc.encode(SetTerminalCommand('ping')))
                                                                     
            ard.flushInput()
            ard.flushOutput()
            
                                                                                                          
            
            while True:
                ser.write(pyvesc.encode(SetAlive))                                                                    
                ser.write(pyvesc.encode_request(GetValues))                                                    
                
                

                time.sleep(0.01)
                
                # Check if there is enough data back for a measurement                                
                while (True):
                  while ser.in_waiting > 0:                   
                    inbuf += ser.read(ser.in_waiting)                                   
                  if len(inbuf) == 0: break
                  

                  while ard.in_waiting > 0:                   
                    inard += ard.read(ard.in_waiting)                                   
                  if len(inard) == 0: break      
                  ard_remain = inard.rsplit(b'\r\n', 1)  # [0]
                  inard = ard_remain[-1]
                  if len(ard_remain) <= 1:
                    break
                  ard_messages = ard_remain[-2].split(b'\r\n')
                

                  #print(ard_messages)

                  ard_values = []
                  if len(ard_messages) >= 1:
                    ard_values = ard_messages[-1].split(b',')
                  if len(ard_values) < ard_length:
                    print("Not enough dyno commas")
                    break     

                  ard_values = list(map(lambda a: a.decode("utf-8"), ard_values))
                  

                  (response_old, consumed) = pyvesc.decode(inbuf)
                  if consumed == 0: break    

                  # Consume the rest so we get the most recent (VESC sends faster than Arduino)
                  response = response_old
                  message_thrown_out = 0
                  while consumed != 0:  
                    response_old = response                          
                    inbuf = inbuf[consumed:]   
                    (response, consumed) = pyvesc.decode(inbuf)
                    message_thrown_out += 1
                  response = response_old

                  print("Vesc messages thrown out {}".format(message_thrown_out))
                  



                  dataAvail = len(inbuf)
                  #print("response " + str(response.id))                             
                  if isinstance(response, GetFirmwareVersion):                                
                    print("Firmware: " + str(response.version_major) + ", " + str(response.version_minor))
                  elif isinstance(response, GetValues):
                    
                    # tacho: one rotation = (pole_counts * 3) 
                    #print("pos: " + str(pos) + " T: " + str(response.temp_fet_filtered) + " rpm: "+  str(response.rpm) + " volt: " + str(response.input_voltage) + " curr: " +str(response.avg_motor_current) + " Tachometer:" + str(response.tachometer_value) + " Tachometer ABS:" + str(response.tachometer_abs_value) + " Duty:" + str(response.duty_cycle_now) + " Watt Hours:" + str(response.watt_hours) + " Watt Hours Charged:" + str(response.watt_hours_charged) + " amp Hours:" + str(response.amp_hours) + " amp Hours Charged:" + str(response.amp_hours_charged) + " avg input current:" + str(response.avg_input_current) )
                    '''print(" Fet temp C: " + str(ctof(response.temp_fet_filtered)) + 
                      " motor temp C: " + str(ctof(response.temp_motor_filtered)) +
                      " In volt: " + str(response.input_voltage) + 
                      " motor curr: " +str(response.avg_motor_current) + 
                      " avg input current:" + str(response.avg_input_current) +
                      " Duty:" + str(response.duty_cycle_now) + 
                      #" Watt Hours:" + str(response.watt_hours) + 
                      #" Watt Hours Charged:" + str(response.watt_hours_charged) + 
                      #" amp Hours:" + str(response.amp_hours) + 
                      #" amp Hours Charged:" + str(response.amp_hours_charged) + 
                       "")'''
                    ard_values.append(str(ctof(response.temp_fet_filtered)))
                    ard_values.append(str(ctof(response.temp_motor_filtered)))
                    ard_values.append(str(response.input_voltage))
                    ard_values.append(str(response.avg_motor_current))
                    ard_values.append(str(response.avg_input_current))
                    ard_values.append(str(response.duty_cycle_now))

                    #print(ard_values)
                    to_print = map(lambda l, v: "{}: {}".format(l,v), labels, ard_values)
                    print("\n".join(to_print))
                    print("\n\n")
                    if f:
                      f.write(",".join(ard_values))
                      f.write("\n")
                  
                  else:
                    print("answer not yet implemented: " + str(response.__class__))
                                            

                  

        except KeyboardInterrupt:
            # Turn Off the VESC
            print ("turning off the VESC...")
            #ser.write(pyvesc.encode(SetCurrent(0)))            
            ser.flushOutput()
            ser.flushInput()
            ser.close()

            ard.flushOutput()
            ard.flushInput()
            ard.close()

            if f:
              f.close()
            

if __name__ == "__main__":
    #signal.signal(signal.SIGINT, signal_handler)    
    get_values_example()