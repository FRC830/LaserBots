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
    def __init__(self, joy_id):
        self.joy = None
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
        else:
            print('Joystick %i not detected' % (joy_id))

    # returns the data that the server should send to the car
    # right now returns a tuple of two floats (speed, turn)
    # use the input_format variable
    # the main loop calls this every cycle
    def data_to_send(self):
        if self.joy:
            # arbitrary controls for now
            speed = joy.get_axis(1)
            turn = joy.get_axis(4)
            return (speed, turn)
        else:
            return (0.0, 0.0)

    # takes the data sent by the car
    # the main loop calls this every cycle
    # which will tell us whether it hit the other car, and possibly other things
    def accept_data(self, data):
        print(self, data)
