# Server
from __future__ import print_function

import socket

import lib.comm as comm
import car_controller

HOST = ''
PORTS = (50001, 50010)

class Dispatcher(comm.Dispatcher):
    client_data = {}
    def next_id(self):
        id = 0
        for c in self.client_data.values():
            if id == c['controller'].id:
                id += 1
        return id
    def connect(self, client):
        print('client connected: %s:%s' % client.addr)
    def disconnect(self, client):
        print('client disconnected: %s:%s' % client.addr)
        if client in self.client_data:
            del self.client_data[client]
    def loop(self, client):
        if not client in self.client_data:
            # Not yet initialized
            return
        client_type = self.client_data[client]['type']
        if client_type == 'car':
            self.client_data[client]['controller'].loop()
    def message(self, client, data):
        if type(data) == dict:
            if data.has_key('init'):
                if data['type'] == 'car':
                    self.init_car(client)
                return
        if self.client_data[client]['type'] == 'car':
            self.client_data[client]['controller'].accept_data(data)
    def init_car(self, client):
        self.client_data[client] = {
            'controller': car_controller.CarController(
                joy_id = self.next_id(),
                client = client,
                dispatcher = self,
            ),
            'type': 'car',
        }
        for c in self.clients:
            self.client_data[c]['controller'].controller_list = \
                [c2['controller'] for c2 in self.client_data.values()]


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
            server = comm.Server(HOST, port)
            break
        except socket.error as e:
            if e.errno in (48, 10048):
                print('- Port %i unavailable' % port)
            else:
                print('Fatal: Failed to initialize server: %s' % e)
                return
    if not server:
        print('Fatal: Could not find any open ports between %i and %i' % PORTS)
        return
    Dispatcher().bind(server)
    try:
        main_server(server)
    finally:
        server.socket.close()

if __name__ == '__main__':
    main()
