#!/usr/bin/env python

import RPi.GPIO as GPIO
import serial
import time

RED_PILL = '/dev/ttyACM0'
BLUE_PILL = '/dev/ttyACM1'

# Serial comms from Dawn
# TODO: correct port??
ser = serial.Serial(
  port='/dev/ttyACM0',
  baudrate = 9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=2
)

button_colors = {
  "btw" : "WHITE",
  "btg" : "GREEN",
  "bty" : "YELLOW",
  "btb" : "BLUE",
  "blb" : "SMALL BLUE",
  "blg" : "SMALL GREEN",
  "blk" : "SMALL BLACK"}

if __name__ == "__main__":
  while True:
    time.sleep(0.05)
    pill_1 = ser.readline()
    if pill_1:
      peripherals = pill_1.split(",")
      for p in peripherals:
        k, v = p.split(":")
#        if v == "0":
#          if k in button_colors:
#            print "pressed ", button_colors[k]
        print "k: ", k, " v: ", v
