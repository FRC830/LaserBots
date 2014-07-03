import RPi.GPIO as gpio
gpio.setmode(gpio.BOARD)

# hopefully this will run on the Pi and control victors and Servos
class Victor(object):
    def __init__(self, pin = 12, freq = 100):
        self.pin = pin
        self.freq = freq
        gpio.setup(self.pin, gpio.OUT)
        
        self.victor = gpio.PWM(self.pin, self.freq)
        self.duty_cycle = 0
        self.victor.start(self.duty_cycle)
        
    def set_duty_cycle(self, dc):
        self.duty_cycle = dc
        self.victor.ChangeDutyCycle(dc)

    def get_duty_cycle(self):
        return self.duty_cycle

    def set_speed(self, speed):
        if speed > 1.0:
            speed = 1.0
            exit()
        if speed < -1.0:
            speed = -1.0

        if speed == 0:
            self.set_duty_cycle(0)
        else:
            self.set_duty_cycle((self.freq/100.0)*(-7.5*speed + 13.9))
        #0 ->13.9
        #-1->20
        #1 ->5
        #y=mx+b
        #b=13.9
        #m = 15/2 = 7.5

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
        gpio.setup(self.pin1 , gpio.OUT)
        gpio.setup(self.pin2 , gpio.OUT)
    def run_fwd(self):
        #run spike in one direction "forward"
        gpio.output(self.pin1, True)
        gpio.output(self.pin2, False)
    def run_bwd(self):
        #run spike in other direction
        gpio.output(self.pin1, False)
        gpio.output(self.pin2, True)
    def stop(self):
        #stop spike output
        gpio.output(self.pin1, False)
        gpio.output(self.pin2, False)

class LineBreak(object):
    """a line break sensor"""
    #http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python/
    def __init__(self, DI = 16):
        """default to digital input on pin 16 (GPIO pin 23)"""
        self.pin = DI
        gpio.setup(self.pin, gpio.IN, pull_up_down = gpio.PUD_DOWN)
    def get(self):
        return gpio.input(self.pin)

class Transistor(object):
    """basic transistor"""
    def __init__(self, pin = 13):
        self.pin = pin
        gpio.setup(self.pin, gpio.OUT)
    def set(self, val):
        gpio.output(self.pin, bool(val))

def cleanup():
    gpio.cleanup()
