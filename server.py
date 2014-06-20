#!/usr/bin/env python

#This is the program that runs on the laptop and sends information from the joysticks to the raspberry pis on the cars
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM
import sys
PORT_NUMBER = 5000
SIZE = 1024

hostName = gethostbyname( '0.0.0.0' )

mySocket = socket( AF_INET, SOCK_DGRAM )
mySocket.bind( (hostName, PORT_NUMBER) )

print ("Test server listening on port {0}\n".format(PORT_NUMBER))

while True:
        (data,addr) = mySocket.recvfrom(SIZE)
        print data
sys.ext()
