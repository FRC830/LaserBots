import RPi.GPIO as gpio
import time

def pulse_len(angle):
	#in seconds
    return (-0.000011111111111111*angle + 0.0021)

pin = 11

gpio.setmode(gpio.BOARD)
gpio.setup(pin , gpio.OUT)

servo = gpio.PWM(pin, 50)
servo.start(12.5)


def set(angle):
	pulse = -0.0527777777*angle+10.083333333333333
	servo.ChangeDutyCycle(pulse)

for i in range(10):
	val = int(input("Angle?"))
	set(val)

print ("done")
#0.0020:10
#0.0015:50
#0.0010:95
#0.0005:135
#0.0000:180
