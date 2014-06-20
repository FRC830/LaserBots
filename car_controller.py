#!/usr/bin/env python

#this collects user input for each car and processes it to be sent to the pi
#each instance of this class corresponds to a car
#this will interact with the gui
#the server should call data_to_send() and send the output to the car
#then take input from the car and give it as input to data_received()

import pygame as pg

class CarController:
    #id is which car this is: 1 or 2
    #higher numbers are possible, we're just only planning to make 2 cars
    def __init__(self, id):
        self.id = id
        if pg.joystick.get_count() >= id:
            self.joy = pg.joystick.Joystick(id-1)
        else:
            print('Joystick %i not detected' % id)
            self.joy = None

        
    #the format for the return value of the get_input function
    input_format = "%f,%f;" #speed, turn

    #returns the string that the server should send to the car
    #right now returns "speed" and "turn" values
    #use the input_format variable
    #the main loop calls this every cycle
    def data_to_send():
        if self.joy:
            #arbitrary controls for now
            speed = joy.get_axis(1)
            turn = joy.get_axis(4)
            return (input_format % (speed, turn))
        else:
            return (input_format % (0.0, 0.0))

    #takes the string sent by the car
    #the main loop calls this every cycle
    #which will tell us whether it hit the other car, and possibly other things
    def data_received(data):
        #just print the data for now, we'll do stuff with it later
        if data:
            print(data)
        return
