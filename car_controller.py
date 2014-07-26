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
    #how fast we slow down when not actively braking
    DRIFT_BRAKE = 2.0
    #limit on braking speed
    MAX_BRAKE = 1.0
    #limit on acceleration backwards
    MAX_REVERSE_ACCEL = 5.0
    
    #these constants are the max value (from 0.0 to 1.0) allowed for speeds
    MAX_FORWARD_SPEED = 0.8
    #all of these should be positive, even for reverse speeds
    #we'll negate the constants as appropriate when we use them
    MAX_REVERSE_SPEED = 0.5

    MAX_CHARGE = 5.0 #time after which charging power has no effect
    FIRE_TIME = 0.25 #time a single shot lasts
    
    def __init__(self, joy_id, client, dispatcher):
        pg.init()
        self.joy = None
        self.health = 50
        self.other_car_health = 50 #it's easier for each car to keep track of the other's health

        self.cycle_length = comm.TICK_INTERVAL  #not sure how accurate TICK_INTERVAL is
        self.last_time = time.time()            #tracking manually instead
        
        self.last_speed = 0.0
        self.last_fire_time = time.time() #time when we last started firing
        self.charge_start_time = time.time() #time we last started charging
        self.charge = 0.0
        self.last_shot_charge = 0.0
        self.charging = False
        self.firing = False
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
        return (1.0 * self.cycle_length) / max_accel
    
            
    def curve_accel(self, input, brake=False):
        """
        Limits acceleration based on the acceleration constants.
        input is the target speed taken from the controller, from -1.0 to 1.0
        returns the new speed from -1.0 to 1.0
        """
        new_speed = -self.joy.get_axis(LEFT_Y)
        #this is the most the speed can increase by to reach 1.0 in MAX_ACCEL_TIME
        #1.0 represents the maximum possible speed (1.0 for us)
        if self.last_speed < 0.0:
            if input > 0.0 or brake:
                max_inc_speed = self.max_delta_speed(self.MAX_BRAKE)
            else:
                max_inc_speed = self.max_delta_speed(self.DRIFT_BRAKE)
        else:
            max_inc_speed = self.max_delta_speed(self.MAX_FORWARD_ACCEL)
        if self.last_speed > 0.0:
            if input < 0.0 or brake:
                max_dec_speed = self.max_delta_speed(self.MAX_BRAKE)
            else:
                max_dec_speed = self.max_delta_speed(self.DRIFT_BRAKE)
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
        if speed < 0.05 and speed > -0.05:
            speed = 0.0
        return speed

    # the main loop calls this every cycle
    def loop(self):
        pg.event.pump()
        data = {}
        if self.joy:
            #negative values are up on the y-axes
            if self.joy.get_button(BUTTON_A):
                data['speed'] = self.curve_accel(0.0, True)
            else:
                data['speed'] = self.curve_accel(-self.joy.get_axis(RIGHT_Y))
            data['turn'] = self.joy.get_axis(LEFT_X)
            charge_pressed = self.joy.get_button(BUTTON_LB) or self.joy.get_button(BUTTON_RB)
            #make each fire last for a certain amount of time
            #charge while button pressed
            if not self.firing:
                if charge_pressed:
                    if not self.charging:
                        self.charge_start_time = time.time()
                        self.charging = True
                    else:
                        self.charge = time.time() - self.charge_start_time
                        if self.charge > CarController.MAX_CHARGE:
                            self.charge = CarController.MAX_CHARGE
                else:
                    if self.charge > 0.0:
                        #fire a shot
                        self.firing = True
                        data['start_fire'] = True
                        self.last_fire_time = time.time()
                        self.charge_of_shot = self.charge
                        self.charge = 0.0

            if self.firing:
                data['fire'] = True
                if time.time() - self.last_fire_time > CarController.FIRE_TIME:
                    self.firing = False

            print("%f %f" % (data['speed'], data['turn']))
            data['spark'] = self.joy.get_button(BUTTON_Y)
            if self.firing:
                data['color'] = (True, False, False) #red
            else:
                data['color'] = (True, True, True) #white
        else:
            #no joystick detected, so give reasonable "do nothing" values
            data['speed'] = 0.0
            data['turn'] = 0.0
        self.send(data)
        self.cycle_length = time.time() - self.last_time
        self.last_time = time.time()

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
            if 'hit_car' in data and data['hit_car']:
                damage = self.last_shot_charge
                if damage > 0.0 and damage < 0.5:
                    damage = 0.5
                self.other_car_health -= damage
                self.last_shot_charge = 0.0 #zero out charge so shots count once
                self.send_to_other({'health': self.other_car_health})
                if self.other_car_health <= 0.0:
                    self.send_to_all({'game_over': True, 'winner': self.id})
                    
            if 'health' in data:
                self.health = data['health']
                self.send({'health': data['health']})
