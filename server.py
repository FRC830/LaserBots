#!/usr/bin/env python

import socket
import sys
import threading

HOST = ''
PORT = 50007

class Server:
    """ Basic socket server """
    def __init__(self, host, port):
        self.lock = threading.Lock()
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(4)

    def serve_forever(self):
        while True:
            ClientHandler(self, *self.socket.accept()).start()

class ClientHandler(threading.Thread):
    def __init__(self, server, client_socket, remote_address):
        super(ClientHandler, self).__init__()
        self.server, self.socket, self.addr = server, client_socket, remote_address

    def run(self):
        self.server.lock.acquire()
        self.server.clients.append(self)
        self.server.lock.release()
        print('* %s:%s connected' % self.addr)
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            print('%s:%s: %s' % (self.addr[0], self.addr[1], data))
        self.socket.close()
        print '* %s:%s disconnected.' % self.addr
        self.server.lock.acquire()
        self.server.clients.remove(self)
        self.server.lock.release()

def main():
    try:
        print('Starting server on %s:%s...' % (HOST, PORT))
        server = Server(HOST, PORT)
    except socket.error as e:
        print('Failed to initialize server: %s' % e)
        return False
    try:
        server.serve_forever()
    except Exception as e:
        print('%s: %s' % (type(e), e))
        return False
    except KeyboardInterrupt, SystemExit:
        print('\nExiting')
        return True

if __name__ == '__main__':
    if not main():
        sys.exit(1)
