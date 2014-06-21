# Server
from __future__ import print_function

import socket

import lib.comm as comm
import car_controller

HOST = ''
PORTS = (50001, 50010)

class Dispatcher(comm.Dispatcher):
    def connect(self, client):
        print('client connected: %s:%s' % client.addr)
        client.info = {
            'controller': car_controller.CarController(
                joy_id = len(self.clients) - 1, # joysticks are 0-indexed
                client = client,
                dispatcher = self,
            )
        }
        for c in self.clients:
            c.info['controller'].controllers = [c2.info['controller']
                                                for c2 in self.clients]
    def disconnect(self, client):
        print('client disconnected: %s:%s' % client.addr)
    def loop(self, client):
        client.info['controller'].loop()
    def message(self, client, data):
        client.info['controller'].accept_data(data)

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
