#!/usr/bin/env python

# runs on the client side
# this class takes the user input and actually controls the car
# this is where all the motor and servo controlling stuff will go eventually
# each instance of this class corresponds to a car

import random

class Car:
    def __init__(self, client):
        self.client = client
        self.hits = 0

    # called every tick - sends data to server
    def loop(self):
        data = {}
        if random.randint(1, 100) == 1:
            self.hits += 1
            data['hit_car'] = self.hits
            print("I hit a car! Hits: %i" % self.hits)
        self.send(data)

    def send(self, data):
        self.client.send(data)

    # takes the data sent by the server
    # which will be processed user input
    # this is the equivalent of our TeleopInit(), kind of
    # where we run all the motors and everything
    def accept_data(self, data):
        if type(data) == dict:
            if data.has_key('health'):
                print("I've been hit! Current health: %i" % data['health'])

