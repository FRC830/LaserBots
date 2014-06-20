#!/usr/bin/env python

#runs on the client side
#this class takes the user input and actually controls the car
#this is where all the motor and servo controlling stuff will go eventually
#each instance of this class corresponds to a car

class Car:
    #returns the string that should be sent to the server
    #tells whether the car hit another with the laser, and possibly other things
    def data_to_send(self):
        return "hi"

    #takes the data sent by the server
    #which will be processed user input
    #this is the equivalent of our TeleopInit(), kind of
    #where we run all the motors and everything
    def accept_data(self, data):
        #print the data for now, later we'll do stuff with it
        if data:
            print(self, data)

