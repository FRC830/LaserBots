#!/usr/bin/env python

from __future__ import print_function

__metaclass__ = type  # Use new-style classes

import errno
import socket
import sys
import threading
import time
import pickle
import zlib
import pygame as pg

from contextlib import contextmanager

TIMEOUT = 0.1
TICK_INTERVAL = 0.002
SOCKET_CLOSED = (errno.EBADF, errno.EPIPE, errno.ECONNRESET)
SOCKET_NO_DATA = (errno.EAGAIN, )

def encode_message(data):
    return zlib.compress(pickle.dumps(data, 2))

def decode_message(data):
    return pickle.loads(zlib.decompress(data))

class SocketConnection(threading.Thread):
    def __init__(self, socket):
        super(SocketConnection, self).__init__()
        socket.settimeout(TIMEOUT)
        self.socket = socket
        self.disconnect = False
        self.send_queue = []
        self.recv_queue = []
        self.lock = threading.Lock()

    def run(self):
        try:
            while not self.disconnect:
                self.tick()
                data = None
                try:
                    self.socket.send(encode_message(self.send_queue))
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
                self.recv_queue.extend(data)
            self.socket.close()
        finally:
            self.close()

    def tick(self):
        """ Called every cycle before sending/receiving data """
        pass

    def send(self, msg):
        with self.lock:
            self.send_queue.append(msg)

    def recv(self):
        with self.lock:
            tmp_queue = self.recv_queue
            self.recv_queue = []
            return tmp_queue

    def close(self):
        self.disconnect = True

class Server:
    """ Basic socket server """
    def __init__(self, host, port):
        self.addr = (host, port)
        self.lock = threading.Lock()
        self.clients = []
        self.disconnect = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(4)
        self._callbacks = {
            'connect': [],
            'disconnect': [],
            'message': [],
            'tick': [],
        }

    def serve_forever(self):
        while not self.disconnect:
            ClientHandler(self, *self.socket.accept()).start()

    def send_message(self, msg, clients):
        for c in clients:
            c.send(msg)

    def add_client(self, client):
        with self.lock:
            self.clients.append(client)
        self._trigger_callbacks('connect', client)

    def remove_client(self, client):
        with self.lock:
            if client in self.clients:
                self.clients.remove(client)
        self._trigger_callbacks('disconnect', client)

    def terminate(self):
        for c in self.clients:
            c.close()
        self.disconnect = True
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
        with self.lock:
            if event in self._callbacks:
                for func in self._callbacks[event]:
                    func(*data)
            else:
                raise ValueError('Unknown event: %r' % event)

class ClientHandler(SocketConnection):
    """ Server-side client """
    def __init__(self, server, client_socket, remote_address):
        super(ClientHandler, self).__init__(client_socket)
        self.server, self.addr = server, remote_address

    def run(self):
        self.server.add_client(self)
        super(ClientHandler, self).run()
        self.server.remove_client(self)

    def tick(self):
        received = self.recv()
        self.server._trigger_callbacks('tick', self)
        for msg in received:
            self.server._trigger_callbacks('message', self, msg)

class Client(SocketConnection):
    """ Client-side client """
    def __init__(self, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)
        super(Client, self).__init__(self.socket)
        self.addr = addr
        self.on_connect()

    def run(self):
        super(Client, self).run()
        self.on_disconnect()

    def listen_forever(self):
        self.start()
        while not self.disconnect:
            time.sleep(TICK_INTERVAL)
            self.on_loop()
            received = self.recv()
            for msg in received:
                self.on_message(msg)

    def on_connect(self): pass
    def on_disconnect(self): pass
    def on_message(self, data): pass
    def on_loop(self): pass


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
