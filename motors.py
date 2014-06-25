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
        if speed < -1.0:
            speed = -1.0

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
        self.servo.start(6)#starting duty cycle
    def set_angle(self, angle):
        """sets duty cycle based on an angle"""
        self.angle = angle
        pulse = -0.0488888888888888 * self.angle + 11
        self.servo.ChangeDutyCycle(pulse)
    def set_duty_cycle(self, dc):
        """for testing only"""
        self.servo.ChangeDutyCycle(dc)