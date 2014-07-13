#!/usr/bin/env python

#runs on the server side
#this collects user input for each car and processes it to be sent to the pi
#each instance of this class corresponds to a car
#this will interact with the gui
#the server should call data_to_send() and send the output to the car
#then take input from the car and give it as input to data_received()

import sys
import time
import pygame as pg
pg.joystick.init()

import lib.comm as comm

#y axes are positive down, negative up
#x axes are positive left, negative right
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
    #these constants are seconds it takes to go from zero to full speed
    #or from full speed to zero for braking
    #so greater numbers => slower acceleration/deceleration
    #limit on acceleration forwards
    MAX_FORWARD_ACCEL = 3.0
    #limit on braking speed
    MAX_BRAKE = 1.0
    #limit on acceleration backwards
    MAX_REVERSE_ACCEL = 3.0
    
    #these constants are the max value (from 0.0 to 1.0) allowed for speeds
    MAX_FORWARD_SPEED = 0.8
    #all of these should be positive, even for reverse speeds
    #we'll negate the constants as appropriate when we use them
    MAX_REVERSE_SPEED = 0.5

    ENUM_NOT_FIRING = 0
    ENUM_FIRING = 1
    ENUM_CHARGING = 2

    FIRE_TIME = 0.25 #seconds
    CHARGE_TIME = 2.0 #seconds to recharge from zero to full
    FIRE_CHARGE = 0.5 #amount of charge taken by each shot
    
    def __init__(self, joy_id, client, dispatcher):
        pg.init()
        self.joy = None
        self.last_speed = 0.0
        self.last_fire_time = 0.0 #time when we last started firing
        self.charge_start_time = 0.0 #time we last started charging; value should be changed before use
        self.charge_remaining = CarController.CHARGE_TIME #seconds
        self.last_charge = CarController.CHARGE_TIME
        self.firing = CarController.ENUM_NOT_FIRING
        self.client, self.dispatcher = client, dispatcher
        self.id = joy_id
        self.send({'id': self.id})
        self.controller_list = []  # list of all controllers
        if pg.joystick.get_count() > joy_id:
            self.joy = pg.joystick.Joystick(joy_id)
            self.joy.init()
        else:
            print('Joystick %i not detected' % (joy_id))
            
    def max_delta_speed(self, max_accel):
        #this gives the most the speed can increase by in one cycle
        #so that it takes max_accel seconds to reach full speed
        #1.0 in this equation represents full speed
        return 1.0 / (max_accel * comm.TICK_INTERVAL)
    
            
    def curve_accel(self, input):
        """
        Limits acceleration based on the acceleration constants.
        input is the target speed taken from the controller, from -1.0 to 1.0
        returns the new speed from -1.0 to 1.0
        """
        new_speed = -self.joy.get_axis(LEFT_Y)
        #this is the most the speed can increase by to reach 1.0 in MAX_ACCEL_TIME
        #1.0 represents the maximum possible speed (1.0 for us)
        max_inc_speed = self.max_delta_speed(self.MAX_FORWARD_ACCEL)
        if self.last_speed > 0.0:
            max_dec_speed = self.max_delta_speed(self.MAX_BRAKE)
        else:
            max_dec_speed = self.max_delta_speed(self.MAX_REVERSE_ACCEL)
        delta_speed = input - self.last_speed
        if delta_speed > max_inc_speed:
            speed = self.last_speed + max_inc_speed
        elif delta_speed < -max_dec_speed:
            speed = self.last_speed - max_dec_speed
        else:
            speed = input
        if speed > self.MAX_FORWARD_SPEED:
            speed = self.MAX_FORWARD_SPEED
        elif speed < -self.MAX_REVERSE_SPEED:
            speed = -self.MAX_REVERSE_SPEED
        self.last_speed = speed
        return speed

    # the main loop calls this every cycle
    def loop(self):
        pg.event.pump()
        start_fire = False
        if self.joy:
            #negative values are up on the y-axes
            speed = self.curve_accel(-self.joy.get_axis(RIGHT_Y))
            turn = self.joy.get_axis(LEFT_X)
            fire = self.joy.get_button(BUTTON_LB) or self.joy.get_button(BUTTON_RB)
            #make each fire last for a certain amount of time
            #and limit the total amount of shots until you must recharge
            #also tell the client if we're beginning a new fire because that's when it'll play the sound effect
            if self.firing == CarController.ENUM_NOT_FIRING:
                if fire and self.charge_remaining >= CarController.FIRE_CHARGE:
                    self.charge_remaining -= CarController.FIRE_CHARGE
                    self.last_fire_time = time.time()
                    self.firing = CarController.ENUM_FIRING
                    start_fire = True
                else:
                    self.charge_remaining = self.charge_remaining + (time.time() - self.charge_start_time)
                    if self.charge_remaining > CarController.CHARGE_TIME:
                        self.charge_remaining = CarController.CHARGE_TIME
                        self.firing = CarController.ENUM_NOT_FIRING
            if self.firing == CarController.ENUM_FIRING:
                if time.time() - self.last_fire_time > CarController.FIRE_TIME:
                    self.firing = CarController.ENUM_NOT_FIRING
                    self.charge_start_time = time.time()
                    self.last_charge = self.charge_remaining
        else:
            speed = 0
            turn = 0
        data = {'speed': speed, 'turn': turn}
        if self.firing == CarController.ENUM_FIRING:
            data['fire'] = True
        if start_fire:
            data['start_fire'] = True
        self.send(data)

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
            if 'hit_car' in data:
                self.send_to_other({'health': -1})
            if 'health' in data:
                health = data['health']
                if health <= 0:
                    self.send_to_all({'game_over': True, 'winner': 1 - self.id})
