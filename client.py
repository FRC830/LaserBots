#!/usr/bin/env python

#This is the program that runs on each car and takes input from the control laptop

import sys
import time
import socket

SERVER_IP   = sys.argv[1] if len(sys.argv) > 1 else raw_input('Remote IP: ')
PORT_NUMBER = 50007
SIZE = 1024

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as e:
    print('Failed to connect to server (%s)' % SERVER_IP)
    sys.exit()
sock.connect((SERVER_IP,PORT_NUMBER))
sock.sendall('Hello, world')

sock.close()
