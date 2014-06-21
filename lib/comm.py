#!/usr/bin/env python

from __future__ import print_function

__metaclass__ = type  # Use new-style classes

import socket
import sys
import threading
import time
import pickle
import zlib
import pygame as pg

from contextlib import contextmanager

TIMEOUT = 0.1
SOCKET_CLOSED = (9, 32, 54)
SOCKET_NO_DATA = (35, 10035)

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
            'loop': [],
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

    def add_dispatcher(self, dispatcher, prefix=''):
        for event in self._callbacks:
            if hasattr(dispatcher, prefix + event):
                self.add_callback(event, getattr(dispatcher, prefix + event))

    def _trigger_callbacks(self, event, *data):
        """ Triggers all callbacks bound to event """
        with self.obtain_lock():
            if event in self._callbacks:
                for func in self._callbacks[event]:
                    func(*data)
            else:
                raise ValueError('Unknown event: %r' % event)

class ClientHandler(threading.Thread):
    """ Server-side client """
    def __init__(self, server, client_socket, remote_address):
        super(ClientHandler, self).__init__()
        self.server, self.socket, self.addr = server, client_socket, remote_address
        self.socket.settimeout(TIMEOUT)
        self.disconnect = False
        self.send_queue = []
        self.info = {}

    def run(self):
        # this runs in a separate thread for each client
        self.server.add_client(self)
        while not self.disconnect:
            self.server._trigger_callbacks('loop', self)
            data = None
            try:
                for msg in self.send_queue:
                    msg = encode_message(msg)
                    self.socket.send(msg)
                self.send_queue = []
                data = self.socket.recv(1024)
            except socket.timeout:
                pass
            except socket.error as e:
                if e.errno in SOCKET_CLOSED:
                    # Client closed
                    break
                elif e.errno in SOCKET_NO_DATA:
                    # No data
                    continue
                else:
                    raise
            if data is None:
                continue
            if data == '':
                break
            data = decode_message(data)
            self.server._trigger_callbacks('message', self, data)
        self.socket.close()
        self.server.remove_client(self)

    def send(self, data):
        self.send_queue.append(data)

    def close(self):
        self.disconnect = True

class Client:
    """ Client-side client """
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
        self.socket.settimeout(TIMEOUT)
        self.addr = addr
        self.disconnect = False
        self.send_queue = []
        self.on_connect()

    def listen_forever(self):
        while not self.disconnect:
            self.on_loop()
            data = None
            try:
                for msg in self.send_queue:
                    msg = encode_message(msg)
                    self.socket.send(msg)
                self.send_queue = []
                data = self.socket.recv(1024)
            except socket.timeout:
                pass
            except socket.error as e:
                if e.errno in SOCKET_CLOSED:
                    # Client closed
                    break
                elif e.errno in SOCKET_NO_DATA:
                    # No data
                    continue
                else:
                    raise
            if data is None:
                continue
            if data == '':
                break
            data = decode_message(data)
            self.on_message(data)
        self.socket.close()
        self.on_disconnect()

    def on_connect(self): pass
    def on_disconnect(self): pass
    def on_message(self, data): pass

    def send(self, data):
        self.send_queue.append(data)

class Dispatcher:
    def __init__(self):
        self.clients = []
        self.server = None

    def Dispatcher_connect(self, client):
        self.clients.append(client)

    def Dispatcher_disconnect(self, client):
        self.clients.remove(client)

    def bind(self, server):
        server.add_dispatcher(self, prefix='Dispatcher_')
        server.add_dispatcher(self)
        self.server = server

    def send_to(self, client, msg):
        client.send(msg)

    def send_all(self, msg):
        for c in self.clients:
            c.send(msg)
