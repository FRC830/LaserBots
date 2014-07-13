#!/usr/bin/env python

# runs on the client side
# this class takes the user input and actually controls the car
# this is where all the motor and servo controlling stuff will go eventually
# each instance of this class corresponds to a car

from __future__ import print_function

import random, sys, time
import pygame as pg
from components import Victor, Servo, Transistor, LineBreak

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
        self.laser_sound = pg.mixer.Sound("laser.wav")
        
        self.drive_motor = Victor()#pin 12
        self.turn_motor = Servo()#pin 11
        self.spark_motor = Transistor(13)#pin 13
        self.line_break = LineBreak() #pin 16, transistor pin 18
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
    # this is the equivalent of our TeleopInit(), kind of
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
                self.update_health(data['health'])
            if 'fire' in data and data['fire']:
                self.firing = data['fire']
                self.line_break.set(self.firing)
                print('fire!' if self.firing else '     ', end='\r')
                sys.stdout.flush()
            else:
                self.firing = False
            if 'start_fire' in data:
#                self.laser_sound.stop()
                self.laser_sound.play()
            if 'speed' in data:
                self.drive_motor.set_speed(data['speed'])
#                print('speed: %f' % data['speed'])
            if 'turn' in data:
                turn = data['turn']
                #change joystick -1 -> 1 into servo 0 -> 180
                turn = 90 * (turn+1)
                self.turn_motor.set_angle(turn)
#                print('turn: %f' % turn)

    def update_health(self, delta):
        self.health += delta
        self.log("Current health: %i", self.health)
        self.send({'health': self.health})
        if delta < 0:
            #car is taking damage, throw sparks
            self.spark_motor.set(1)
            #control loss sequence

