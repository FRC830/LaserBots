#!/usr/bin/env python

#This is the program that runs on the laptop and sends information from the joysticks to the raspberry pis on the cars
import socket
import sys
PORT_NUMBER = 5000
#SIZE = 1024

HOST = ''
PORT = 50007

import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        # self.request.sendall(self.data.upper())

if __name__ == "__main__":
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()

