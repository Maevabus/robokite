#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2013 Nautilabs
#
# Licensed under the MIT License,
# https://github.com/baptistelabat/robokite
# Authors: Baptiste LABAT
import time
import serial
import numpy as np

def computeXORChecksum(chksumdata):
    # Inspired from http://doschman.blogspot.fr/2013/01/calculating-nmea-sentence-checksums.html
    # Initializing XOR counter
    csum = 0
    
    # For each char in chksumdata, XOR against the previous 
    # XOR char.  The final XOR of the last char will be the
    # checksum  
    for c in chksumdata:
        # Makes XOR value of counter with the next char in line
        # and stores the new XOR value in csum
        csum ^= ord(c)
    h = hex(csum)    
    return h[2:].zfill(2)#get hex data without 0x prefix
    
def NMEA(message_type, value, talker_id= "OR"):
  msg = talker_id + message_type +","+ str(value)
  msg = "$"+ msg +"*"+ computeXORChecksum(msg) + str(chr(13).encode('ascii')) + str(chr(10).encode('ascii'))
  return msg
    
msg1 = NMEA("PW1", 0.00, "OR")
msg2 = NMEA("PW2", 0.00, "OR")
mfb = NMEA("FBR", 0, "OR")
dt = 0.01
locations=['/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyACM4','/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3','/dev/ttyS0','/dev/ttyS1','/dev/ttyS2','/dev/ttyS3']
for device in locations:
  try:
    print("Trying...", device)
    ser = serial.Serial(device, baudrate=19200, timeout=1)
    print("Connected on ", device)
    break
  except:
    print("Failed to connect on ", device)
time.sleep(1.5)
t0 = time.time()
n = 0
while True:
  n = n+1
  t = time.time()-t0
  print("n= ", n, ", t= ", t)
  order = 0.2*np.sin(t)
  alpha = np.round(order, 2)
  msg1 = NMEA("PW1", alpha, "OR")
  msg2 = NMEA("PW2", alpha, "OR")
  print(msg1)
  ser.write(msg1.encode())
  ser.write(msg2.encode())
  print("Message sent")
  try: #The ressource can be temporarily unavailable
    ser.write(mfb.encode())
    line = ser.readline()
    print("Received from arduino: ", line)
  except Exception as e:
    print("Error reading from serial port" + str(e))
      
  time.sleep(dt)
ser.close()
