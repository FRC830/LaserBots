#!/usr/bin/env python

#runs on the server side
#this collects user input for each car and processes it to be sent to the pi
#each instance of this class corresponds to a car
#this will interact with the gui
#the server should call data_to_send() and send the output to the car
#then take input from the car and give it as input to data_received()

import pygame as pg
pg.joystick.init()

class CarController:
    def __init__(self, joy_id, client, dispatcher):
        self.joy = None
        self.client, self.dispatcher = client, dispatcher
        self.id = joy_id
        self.send({'id': self.id})
        self.controller_list = []  # list of all controllers
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
        else:
            print('Joystick %i not detected' % (joy_id))

    # the main loop calls this every cycle
    def loop(self):
        if self.joy:
            # arbitrary controls for now
            speed = joy.get_axis(1)
            turn = joy.get_axis(4)
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
                if health == 0:
                    self.send_to_all({'game_over': True, 'winner': 1 - self.id})
