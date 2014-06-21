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
    #static variable to keep track of which car we're on
    #so each one can be assigned a separate controller
    n_cars = 0

    def __init__(self):
        joy_id = CarController.n_cars
        CarController.n_cars += 1
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
        else:
            print('Joystick %i not detected' % (joy_id + 1))
            self.joy = None


    #returns the data that the server should send to the car
    #right now returns a tuple of two floats (speed, turn)
    #use the input_format variable
    #the main loop calls this every cycle
    def data_to_send(self):
        if self.joy:
            #arbitrary controls for now
            speed = joy.get_axis(1)
            turn = joy.get_axis(4)
            return (speed, turn)
        else:
            return (0.0, 0.0)

    #takes the string sent by the car
    #the main loop calls this every cycle
    #which will tell us whether it hit the other car, and possibly other things
    def accept_data(self, data):
        #just print the data for now, we'll do stuff with it later
        if data:
            print(data)
        return
