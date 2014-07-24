import RPi.GPIO as gpio
gpio.setmode(gpio.BOARD)

import wiringpi2 as wp
wp.wiringPiSetupPhys()

import os
if os.geteuid() != 0:
    print('WARNING: Not root')


# controls a victor
# must use the hardware pwm on physical pin 12
class Victor(object):
    def __init__(self, freq = 100.0):
        self.freq = freq
        wp.pinMode(12, 2) #set pin 12 to pwm mode
        wp.pwmSetRange(4000) #range can go up to 4096, 4000 is good because it's large and a multiple of 100
        clock = 19.2e6 / (4000.0 * freq) #set the divisor so the frequency comes out right
        wp.pwmSetClock(int(clock)) #this function needs an int
	wp.pwmSetMode(0) # necessary or else it's in a weird mode where nothing works
	wp.pwmWrite(12, 0) # stop for safety

    def set_speed(self, speed):
        if speed > 1.0:
            speed = 1.0
        if speed < -1.0:
            speed = -1.0
        # this results in speeds from 500 (fastest allowed forward)
        # to 700 (fastest allowed reverse)
        duty_cycle = 600 - (100 * speed)
	wp.pwmWrite(12, int(duty_cycle)) # this also wants an int
        return duty_cycle    

class Servo(object):
    def __init__(self, pin = 11):
        gpio.setup(pin , gpio.OUT)
        self.pin = pin
        
        self.servo = gpio.PWM(self.pin, 50)
        self.servo.start(self.angle_to_dc(90))#starting duty cycle
    def set_angle(self, angle):
        """sets duty cycle based on an angle"""
        if angle>180:
		angle = 180
	if angle<0:
		angle = 0
	self.angle = angle
        pulse = self.angle_to_dc(self.angle)
        self.set_duty_cycle(pulse)
    def angle_to_dc(self, angle):
        """compute the duty cycle to give a certain angle"""
        return -0.0488888888888888 * angle + 11
    def set_duty_cycle(self, dc):
        """for testing/internal use only"""
        self.servo.ChangeDutyCycle(dc)

class Spike(object):
    def __init__(self, pin1=13, pin2=15):
        """pin1 = white/signal | pin2 = red/power"""
        self.pin1 = pin1
        self.pin2 = pin2
        wp.pinMode(self.pin1, 1) # output
        wp.pinMode(self.pin2, 1)
    def run_fwd(self):
        #run spike in one direction "forward"\
        wp.digitalWrite(self.pin1, 1)
        wp.digitalWrite(self.pin2, 0)
    def run_bwd(self):
        #run spike in other direction
        wp.digitalWrite(self.pin1, 0)
        wp.digitalWrite(self.pin2, 1)
    def stop(self):
        #stop spike output
        wp.digitalWrite(self.pin1, 0)
        wp.digitalWrite(self.pin2, 0)

class Transistor(object):
    """basic transistor"""
    def __init__(self, pin):
        self.pin = pin
        wp.pinMode(self.pin, 1) # output
    def set(self, val):
        wp.digitalWrite(self.pin, val)


class LineBreak(object):
    """a line break sensor"""
    #http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/
    def __init__(self, input_pin = 16, control_pin = 18):
        """default to digital input on pin 16 (GPIO pin 23)"""
        self.pin = input_pin
        gpio.setup(self.pin, gpio.IN, pull_up_down = gpio.PUD_DOWN)
        self.transistor = Transistor(control_pin)
    def set(self, val):
        self.transistor.set(val)
    def broken(self):
        #returns true if the line is broken (probably)
        return gpio.input(self.pin)


def cleanup():
    gpio.cleanup()
    wp.pinMode(12, 0) # set to input
