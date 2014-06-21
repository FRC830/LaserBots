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
        self.id = joy_id
        #the id of the other car, assuming 2 cars
        self.other = 1
        if joy_id == 0:
            self.other = 1
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
        else:
            print('Joystick %i not detected' % (joy_id))


    #the health of the two cars, from 100 counting down to zero
    #having them be static is an ugly solution but it's the easiest way
    #for each car to be able to change the other's health
    #which is necessary because the retroflective linebreak
    #allows a car to detect when it hits another, but not vice versa
    health = (100, 100)
    
    # returns the data that the server should send to the car
    # right now returns a tuple (i_health, f_speed, f_turn)
    # use the input_format variable
    # the main loop calls this every cycle
    def data_to_send(self):
        if self.joy:
            # arbitrary controls for now
            speed = joy.get_axis(1)
            turn = joy.get_axis(4)
            return (CarController.health[self.id], speed, turn)
        else:
            return (CarController.health[self.id], 0.0, 0.0)

    # takes the data sent by the car
    # the main loop calls this every cycle
    # which will tell us whether it hit the other car, and possibly other things
    def accept_data(self, data):
        if data:
            CarController.health[self.other] -= 1
        print(self, data)
