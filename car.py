#!/usr/bin/env python

# runs on the client side
# this class takes the user input and actually controls the car
# this is where all the motor and servo controlling stuff will go eventually
# each instance of this class corresponds to a car

import random

class Car:
    def __init__(self, client):
        self.client = client

    # called every tick - sends data to server
    def loop(self):
        data = {}
        if random.randint(1, 20) == 1:
            data['hit_car'] = True
        self.send(data)

    def send(self, data):
        self.client.send(data)

    #takes the data sent by the server
    #which will be processed user input
    #this is the equivalent of our TeleopInit(), kind of
    #where we run all the motors and everything
    def accept_data(self, data):
        #print the data for now, later we'll do stuff with it
        print(self, data)

