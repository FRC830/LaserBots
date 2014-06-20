#!/usr/bin/env python

#This is the program that runs on the laptop and sends information from the joysticks to the raspberry pis on the cars
import socket
import sys
PORT_NUMBER = 5000
SIZE = 1024

HOST = ''
PORT = 50007

sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
sock.bind( (HOST, PORT) )
sock.listen(1)
conn, addr = sock.accept()
print 'Connected by', addr

while True:
        data = conn.recv(SIZE)
        if not data: break
        print data
conn.close()
