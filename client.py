#!/usr/bin/env python

#This is the program that runs on each car and takes input from the control laptop

import sys
import time
import socket

import lib.comm as comm
import car

try:
    import readline
except ImportError:
    pass

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else raw_input('Remote IP: ')
PORTS = (50001, 50010)
SIZE = 1024

class Client(comm.Client):
    def __init__(self, *args):
        super(Client, self).__init__(*args)
        self.car = car.Car(
            client = self
        )

    def on_connect(self):
        print('Connected to %s:%s' % self.addr)

    def on_message(self, data):
        self.car.accept_data(data)

    def on_loop(self):
        self.car.loop()

    def on_disconnect(self):
        print('Disconnected.')

connected = False
port_connected = PORTS[0]
while not connected:
    for port in range(PORTS[0], PORTS[1] + 1):
        try:
            print('- Trying %s:%i' % (SERVER_IP, port))
            client = Client((SERVER_IP, port))
            connected = True
            port_connected = port
            break
        except socket.error as e:
            print('- Connection failed: %s' % e)

    if not connected:
        print('Could not find server.')
        print('Trying again in 10 seconds...')
        time.sleep(10)

while True:    
    try:
        client.listen_forever()
    except socket.error as e:
        print('- Connection lost: %s' %e)
        connected = False
        while not connected:
            try:
                print('- Trying %s:%i' % (SERVER_IP, port_connected))
                client = Client((SERVER_IP, port_connected))
                connected = True
                break
            except socket.error as e:
                print('- Connection failed: %s' % e)
                time.sleep(1)

