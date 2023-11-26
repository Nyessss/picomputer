import RPi.GPIO as GPIO
import time
import os

BUTTON_PIN = 14
GPIO.setmode(GPIO.BCM)

def button_callback(channel):
	if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
		print("Pin ON")
		os.system("sudo uhubctl -l 1-1 -a 1")
	else:
		print("Pin OFF")
		os.system("sudo uhubctl -l 1-1 -a 0")

GPIO.setup(BUTTON_PIN, GPIO.IN)

GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=button_callback)

try:
	while True:
		time.sleep(0.01)
except KeyboardInterrupt:
	GPIO.cleanup()

	#os.system("sudo uhubctl -l 1-1 -a toggle")
#        os.system("sudo uhubctl -l 1-1 -a toggle")