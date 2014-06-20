import RPi.GPIO as gpio
import time

pin = 11#can be any of the pi's gpio pins (11 and 12 are fine)

gpio.setmode(gpio.BOARD)
gpio.setup(pin , gpio.OUT)

servo = gpio.PWM(pin, 50)
servo.start(7.5)#starting duty cycle

def pulse_len(angle):
    #in seconds
    return (-0.000011111111111111*angle + 0.0021)

def set(angle):
    #this is kind of arbitrary
    pulse = -0.0527777777*angle+10.083333333333333
    servo.ChangeDutyCycle(pulse)

for i in range(10):
	val = int(input("Angle?"))
	set(val)

print ("done")

