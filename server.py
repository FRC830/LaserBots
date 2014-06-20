#!/usr/bin/env python

from __future__ import print_function

import socket
import sys
import threading
import time
import pygame as pg

#these will be set later
joy_count = 0
joys = (None, None)

#the format for the return value of the get_input function
input_format = "%f,%f;" #speed, turn

#controller is 1 or 2 for the first or second
#right now returns "speed" and "turn" values
#return value has to be processed as a float for the convenience of the server
#use the input_format variable
#the main loop calls this every cycle
#this function will also do all the processing we want to do with control input
#eg limiting acceleration and so on
def get_input(controller):
    #if there aren't enough controllers, first re-check for controllers
    #if that doesn't work return whatever means "stop and do nothing"
    if  controller > joy_count:
        joy_count = pg.joystick.get_count()
        if controller > joy_count:
            print('Input missing for car %i' % controller)
        else:
            joys[controller-1] = pg.joystick.Joystick(controller-1)
            return (input_format % (0.0, 0.0))
    joy = joys[controller-1]
    #arbitrary controls for now
    speed = joy.get_axis(1)
    turn = joy.get_axis(4)
    return (input_format % (speed, turn))


from contextlib import contextmanager

HOST = ''
PORTS = (50001, 50010)

class Server:
    """ Basic socket server """
    def __init__(self, host, port):
        self.addr = (host, port)
        self.lock = threading.Lock()
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(4)
        self.callbacks = {
            'connect': [],
            'disconnect': [],
            'message': [],
        }

    def serve_forever(self):
        while True:
            ClientHandler(self, *self.socket.accept()).start()

    @contextmanager
    def obtain_lock(self):
        self.lock.acquire()
        yield
        self.lock.release()

    def add_client(self, client):
        with self.obtain_lock():
            self.clients.append(client)
            print('* %s:%s connected' % client.addr)

    def remove_client(self, client):
        with self.obtain_lock():
            if client in self.clients:
                self.clients.remove(client)
                print('* %s:%s disconnected' % client.addr)

    def terminate(self):
        for c in self.clients:
            c.close()
        self.socket.close()

    def add_callback(self, event, func):
        if not hasattr(func, '__call__'):
            raise TypeError('Function must be callable')
        if event in self.callbacks:
            if not func in self.callbacks[event]:
                self.callbacks[event].append(func)
            else:
                raise ValueError('Function %r already exists for event %r' % (func, event))
        else:
            raise ValueError('Unknown event: %r' % event)

class ClientHandler(threading.Thread):
    def __init__(self, server, client_socket, remote_address):
        super(ClientHandler, self).__init__()
        self.server, self.socket, self.addr = server, client_socket, remote_address
        self.socket.setblocking(0)
        self.disconnect_flag = False

    def run(self):
        self.server.add_client(self)
        while not self.disconnect_flag:
            data = None
            try:
                data = self.socket.recv(1024)
            except socket.error as e:
                if e.errno == 9:
                    # Client closed
                    break
                elif e.errno == 35:
                    # No data
                    time.sleep(0.01)
                else:
                    raise
            if data is None:
                time.sleep(0.01)
                continue
            if data == '':
                break
            print('%s:%s: %s' % (self.addr[0], self.addr[1], data))
        self.socket.close()
        self.server.remove_client(self)

    def close(self):
        self.disconnect_flag = True

def main_server(server):
    print('Starting server on %s:%s...' % server.addr)
    try:
        server.serve_forever()
    except Exception as e:
        print('%s: %s' % (type(e), e))
        return False, e
    except KeyboardInterrupt, SystemExit:
        print('\nExiting')
        server.terminate()
        return True, None

def main():
    #detect joysticks
    #if we don't have enough, we'll keep looking for joysticks in the main cycle
    pg.init()
    joy_count = pg.joystick.get_count()
    if joy_count == 0:
        print('No joysticks detected')
    elif joy_count == 1:
        print('Only one joystick detected')
        joys[0] = pg.joystick.Joystick(0)
    else:
        print('At least two joysticks detected')
        joys = (pg.joystick.Joystick(0), pg.joystick.Joystick(1))
        
    server = None
    for port in range(PORTS[0], PORTS[1] + 1):
        print('- Trying to bind to port %i...' % port)
        try:
            server = Server(HOST, port)
            break
        except socket.error as e:
            if e.errno == 48:
                print('- Port %i unavailable' % port)
            else:
                print('Fatal: Failed to initialize server: %s' % e)
                return
    if not server:
        print('Fatal: Could not find any open ports between %i and %i' % PORTS)
        return
    try:
        main_server(server)
    finally:
        server.socket.close()

if __name__ == '__main__':
    main()
