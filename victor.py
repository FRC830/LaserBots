# hopefully this will run on the Pi and control victors
import RPi.GPIO as gpio
class Victor(object):
    def __init__(pin=12, freq=100):
        self.pin = pin
        self.freq = freq
        gpio.setmode(gpio.BOARD)
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
        if speed < -1.0:
            speed = -1.0

        self.set_duty_cycle(7.5*speed + 13.9)
        #0 ->13.9
        #-1->20
        #1 ->5
        #y=mx+b
        #b=13.9
        #m = 15/2 = 7.5
            
        
        
