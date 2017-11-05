from threading import Thread
import socket
import time
import RPi.GPIO as GPIO

VERBOSE= = TRUE
IP_PORT = 22000
P_BUTTON = 24

def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(P_BUTTON, GPIO.IN, GPIO.PUD_UP)

def debug(text):
	if VERBOSE:
		print "Debug:---", text

# ------ class SocketHandler -----
class SocketHandler(Thread):
	
