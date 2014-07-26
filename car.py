#!/usr/bin/env python

# runs on the client side
# this class takes the user input and actually controls the car
# this is where all the motor and servo controlling stuff will go eventually
# each instance of this class corresponds to a car

from __future__ import print_function

import random, sys, time
import pygame as pg
from components import Victor, Servo, Transistor, LineBreak, cleanup

RED = 1
GREEN = 1 << 1
BLUE = 1 << 2

class Car:
    def __init__(self, client):
        self.client = client
        self.hits = 0
        self.health = 100
        self.id = -1
        self.firing = False
        self.game_over = False
        self.send({'init': True, 'type': 'car'})

        pg.init()
        self.laser_sound = pg.mixer.Sound('laser.wav')
        
        self.drive_motor = Victor()#has to be pin 12
        self.servo = Servo()#pin 11
        self.spark_motor = Transistor(13)#pin 13
        self.line_break = LineBreak() #input pin 16

        self.red_led = Transistor(3) # pin TBD
        self.green_led = Transistor(5) # pin TBD
        self.blue_led = Transistor(7) # pin TBD
        
    def log(self, msg, *args):
        print(('[Car %i] ' % self.id) + (msg % args))

    # called every tick - sends data to server
    def loop(self):
        if self.game_over:
            return
        data = {}
        if self.firing:
            data['hit_car'] = self.line_break.broken()
        self.send(data)
    def send(self, data):
        self.client.send(data)

    # takes the data sent by the server
    # which will be processed user input
    # this is the equivalent of our TeleopPeriodic(), kind of
    # where we run all the motors and everything
    def accept_data(self, data):
        if type(data) == dict:
            if 'game_over' in data:
                self.game_over = True
                if data['winner'] == self.id:
                    self.log('I win!')
                else:
                    self.log('I lose.')
            if 'id' in data:
                self.id = data['id']
            if 'health' in data:
                if data['health'] - self.health < 0:
                    #car is taking damage, throw sparks
                    self.spark_motor.set(1)
                    #control loss sequence

                    self.health = data['health']               
                    self.log("Current health: %i", self.health)
            if 'fire' in data and data['fire']:
                self.firing = data['fire']
                print('fire!' if self.firing else 'no fire')
            else:
                self.firing = False
            if 'start_fire' in data:
#                self.laser_sound.stop()
                self.laser_sound.play()
            if 'speed' in data:
                # our motor is reversed relative to our forward
                dc = self.drive_motor.set(-data['speed'])
#                print('duty cycle: %f' % dc)
            if 'turn' in data:
		turn = -data['turn']
#		print(turn)
                self.servo.set(turn)
            if 'spark' in data and data['spark']
                self.spark_motor.set(1)
            else:
                self.spark_motor.set(0)
            if 'color' in data:
                color = data['color']
                self.red_led.set(color[0])
                self.green_led.set(color[1])
                self.blue_led.set(color[2])

    def update_health(self, delta):
        self.health += delta
        self.send({'health': self.health})


