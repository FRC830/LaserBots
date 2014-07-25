import wiringpi2 as wp 
wp.wiringPiSetupPhys()

import os
if os.geteuid() != 0:
    print('WARNING: Not root')

INPUT = 0
OUTPUT = 1
PWM = 2
PUD_DOWN = 1
PUD_UP = 2

# controls a victor
# must use the hardware pwm on physical pin 12
class Victor(object):
    def __init__(self, freq = 100.0):
        self.freq = freq
        wp.pinMode(12, PWM)
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

# always pin 11, can be others in theory
# based on ServoBlaster
class Servo(object):
    def __init__(self):
        os.system("echo 1=50% > /dev/servoblaster")
    def set(self, val):
        """sets duty cycle based on a value from -1.0 to 1.0"""
        percent = int((val * 50) + 50)
        if percent>100:
		percent = 100
	if percent<0:
		percent = 0
	print(percent)
	os.system("echo 1=%d%% > /dev/servoblaster" % percent)

class Spike(object):
    def __init__(self, pin1=13, pin2=15):
        """pin1 = white/signal | pin2 = red/power"""
        self.pin1 = pin1
        self.pin2 = pin2
        wp.pinMode(self.pin1, OUTPUT)
        wp.pinMode(self.pin2, OUTPUT)
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
        wp.pinMode(self.pin, INPUT)
        wp.pullUpDnControl(self.pin, PUD_DOWN)
        self.transistor = Transistor(control_pin)
    def set(self, val):
        self.transistor.set(val)
    def broken(self):
        #returns true if the line is broken (probably)
        return wp.digitalRead(self.pin)


def cleanup():
    gpio.cleanup()
    wp.pinMode(12, 0) # set to input
