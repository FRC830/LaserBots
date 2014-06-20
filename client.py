#!/usr/bin/env python

#This is the program that runs on each car and takes input from the control laptop

import sys
import time
import socket

import server
import car

try:
    import readline
except ImportError:
    pass

client_car = car.Car()

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else raw_input('Remote IP: ')
PORTS = (50001, 50010)
SIZE = 1024

sock = None
connected = False
for port in range(PORTS[0], PORTS[1] + 1):
    try:
        print('- Trying %s:%i' % (SERVER_IP, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, port))
        print('Connected successfully.')
        connected = True
        break
    except socket.error as e:
        print('- Connection failed: %s' % e)

if not connected:
    print('Fatal: Could not find server.')
    sys.exit()

while True:
    try:
        data = None
        try:
            data = sock.recv(1024)
            #right now the server isn't sending anything, so this is causing issues
            #data = server.decode_message(data)
        except socket.error as e:
            if e.errno == 35:
                # No data
                time.sleep(0.01)
            else:
                raise
        if data is None:
            time.sleep(0.01)
            continue
        #car.accept_data(data)
        to_send = client_car.data_to_send()
        sock.send(server.encode_message(to_send))
    except KeyboardInterrupt:
        print('')
        break

sock.close()
