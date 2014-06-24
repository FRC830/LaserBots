import RPi.GPIO as gpio

class Servo(object):
    def __init__(self, pin = 11):
        gpio.setmode(gpio.BOARD)
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
