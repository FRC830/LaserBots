#!/usr/bin/env python

from __future__ import print_function

import socket
import sys
import threading
import time
import pickle
import zlib
import pygame as pg

from contextlib import contextmanager

import car_controller

HOST = ''
PORTS = (50001, 50010)

def encode_message(data):
    return zlib.compress(pickle.dumps(data, 2))

def decode_message(data):
    return pickle.loads(zlib.decompress(data))

class Server:
    """ Basic socket server """
    def __init__(self, host, port):
        self.addr = (host, port)
        self.lock = threading.Lock()
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(4)
        self._callbacks = {
            'connect': [],
            'disconnect': [],
            'message': [],
        }

    def serve_forever(self):
        while True:
            ClientHandler(self, *self.socket.accept()).start()

    def send_message(self, msg, clients):
        msg = encode_message(msg)
        for c in clients:
            c.socket.send(msg)

    @contextmanager
    def obtain_lock(self):
        self.lock.acquire()
        yield
        self.lock.release()

    def add_client(self, client):
        with self.obtain_lock():
            self.clients.append(client)
            self._trigger_callbacks('connect', client)

    def remove_client(self, client):
        with self.obtain_lock():
            if client in self.clients:
                self.clients.remove(client)
                self._trigger_callbacks('disconnect', client)

    def terminate(self):
        for c in self.clients:
            c.close()
        self.socket.close()

    def add_callback(self, event, func):
        if not hasattr(func, '__call__'):
            raise TypeError('Function must be callable')
        if event in self._callbacks:
            if not func in self._callbacks[event]:
                self._callbacks[event].append(func)
            else:
                raise ValueError('Function %r already exists for event %r' % (func, event))
        else:
            raise ValueError('Unknown event: %r' % event)

    def _trigger_callbacks(self, event, *data):
        """ Triggers all callbacks bound to event """
        if event in self._callbacks:
            for func in self._callbacks[event]:
                func(*data)
        else:
            raise ValueError('Unknown event: %r' % event)

class ClientHandler(threading.Thread):
    def __init__(self, server, client_socket, remote_address):
        super(ClientHandler, self).__init__()
        self.server, self.socket, self.addr = server, client_socket, remote_address
        self.socket.setblocking(0)
        self.disconnect_flag = False
        #the car controller associated with this client
        self.car_con = car_controller.CarController()

    def run(self):
        self.server.add_client(self)
        #this is the main loop that is run repeatedly
        #one of these is running concurrently for each car
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
            data = decode_message(data)
            self.server._trigger_callbacks('message', self, data)
            #give data from car to the car controller
            car_con.accept_data(data)
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
    server = None
    for port in range(PORTS[0], PORTS[1] + 1):
        print('- Trying to bind to port %i...' % port)
        try:
            server = Server(HOST, port)
            break
        except socket.error as e:
            print('error number %i' % e.errno)
            if e.errno == 10048:
                print('- Port %i unavailable' % port)
            else:
                print('Fatal: Failed to initialize server: %s' % e)
                return
    if not server:
        print('Fatal: Could not find any open ports between %i and %i' % PORTS)
        return
    server.add_callback('connect', lambda client: print('* Connected: %s:%s' % client.addr))
    server.add_callback('disconnect', lambda client: print('* Disconnected: %s:%s' % client.addr))
    server.add_callback('message', lambda client, data: print('%s:%s: %s' % (client.addr[0], client.addr[1], data)))
    try:
        main_server(server)
    finally:
        server.socket.close()

if __name__ == '__main__':
    main()
