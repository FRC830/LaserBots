#!/usr/bin/env python

#runs on the server side
#this collects user input for each car and processes it to be sent to the pi
#each instance of this class corresponds to a car
#this will interact with the gui
#the server should call data_to_send() and send the output to the car
#then take input from the car and give it as input to data_received()

import sys
import pygame as pg
pg.joystick.init()

LEFT_Y = 1
LEFT_X = 0
RIGHT_Y = 3
RIGHT_X = 4
#left bumper positive, right bumper negative
BUMPER_AXIS = 2

BUTTON_A = 0
BUTTON_B = 1
BUTTON_X = 2
BUTTON_Y = 3
BUTTON_LB = 4
BUTTON_RB = 5
BUTTON_BACK = 6
BUTTON_START = 7
LEFT_STICK = 8
RIGHT_STICK = 9


class CarController:
    def __init__(self, joy_id, client, dispatcher):
        pg.init()
        self.joy = None
        self.client, self.dispatcher = client, dispatcher
        self.id = joy_id
        self.send({'id': self.id})
        self.controller_list = []  # list of all controllers
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
            self.joy.init()
        else:
            print('Joystick %i not detected' % (joy_id))

    # the main loop calls this every cycle
    def loop(self):
        pg.event.pump()
        if self.joy:
            #negative values are up on the y-axes
            speed = -self.joy.get_axis(LEFT_Y)
            turn = self.joy.get_axis(RIGHT_X)
        else:
            speed = turn = 0
        self.send({'speed': speed, 'turn': turn})

    def send(self, data):
        self.dispatcher.send_to(self.client, data)

    def send_to_other(self, data):
        for c in self.controller_list:
            if c is not self:
                c.send(data)

    def send_to_all(self, data):
        for c in self.controller_list:
            c.send(data)

    # takes the data sent by the car
    # the main loop calls this every cycle
    # which will tell us whether it hit the other car, and possibly other things
    def accept_data(self, data):
        if type(data) == dict:
            if data.has_key('hit_car'):
                self.send_to_other({'health': -1})
            if data.has_key('health'):
                health = data['health']
                if health <= 0:
                    self.send_to_all({'game_over': True, 'winner': 1 - self.id})
