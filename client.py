#!/usr/bin/env python

#This is the program that runs on each car and takes input from the control laptop

import sys
import time
import socket

SERVER_IP   = raw_input('Remote IP: ')
PORT_NUMBER = 50007
SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP,PORT_NUMBER))
sock.sendall('Hello, world')

sock.close()
