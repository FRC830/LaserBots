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
        self.health = 100
        self.id = None
        self.game_over = False
        self.send({'init': True, 'type': 'car'})

    def log(self, msg, *args):
        print(('[Car %i] ' % self.id) + (msg % args))

    # called every tick - sends data to server
    def loop(self):
        if self.game_over:
            return
        data = {}
        if random.randint(1, 10) == 1:
            self.hits += 1
            data['hit_car'] = True
            self.log("I hit a car! Hits: %i", self.hits)
        self.send(data)

    def send(self, data):
        self.client.send(data)

    # takes the data sent by the server
    # which will be processed user input
    # this is the equivalent of our TeleopInit(), kind of
    # where we run all the motors and everything
    def accept_data(self, data):
        if type(data) == dict:
            if data.has_key('game_over'):
                self.game_over = True
                if data['winner'] == self.id:
                    self.log('I win!')
                else:
                    self.log('I lose.')
            if data.has_key('id'):
                self.id = data['id']
            if data.has_key('health'):
                self.update_health(data['health'])

    def update_health(self, delta):
        self.health += delta
        self.log("Current health: %i", self.health)
        self.send({'health': self.health})

