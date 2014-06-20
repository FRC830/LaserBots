#!/usr/bin/env python

import socket
import sys
import threading
import time

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
        self.callbacks = {
            'connect': [],
            'disconnect': [],
            'message': [],
        }

    def serve_forever(self):
        while True:
            ClientHandler(self, *self.socket.accept()).start()

    def remove_client(self, client):
        self.lock.acquire()
        if client in self.clients:
            self.clients.remove(client)
        self.lock.release()

    def terminate(self):
        for c in self.clients:
            c.socket.shutdown(socket.SHUT_RD)
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
        self.open = False

    def run(self):
        self.open = True
        self.server.lock.acquire()
        self.server.clients.append(self)
        self.server.lock.release()
        print('* %s:%s connected' % self.addr)
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            print('%s:%s: %s' % (self.addr[0], self.addr[1], data))
        self.close()

    def close(self):
        if self.open:
            try:
                #self.socket.shutdown(socket.SHUT_RD)
                self.socket.close()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print('%s' % e)
            self.server.remove_client(self)
            print '* %s:%s disconnected.' % self.addr
            self.open = False

def main(server):
    print('Starting server on %s:%s...' % (HOST, PORT))
    try:
        server.serve_forever()
    except Exception as e:
        print('%s: %s' % (type(e), e))
        return False, e
    except KeyboardInterrupt, SystemExit:
        print('\nExiting')
        server.terminate()
        return True, None

if __name__ == '__main__':
    try:
        server = Server(HOST, PORT)
    except socket.error as e:
        print('Failed to initialize server: %s' % e)
        sys.exit(1)
    try:
        main(server)
    except (Exception, KeyboardInterrupt, SystemExit) as e:
        print(e)
        server.socket.close()
