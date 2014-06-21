# Server
from __future__ import print_function

import socket

import lib.comm as comm
import car_controller

HOST = ''
PORTS = (50001, 50010)

class Dispatcher:
    def __init__(self):
        self.clients = {}
    def connect(self, client):
        print('client connected: %s:%s' % client.addr)
        self.clients[client.ID] = {
            'controller': car_controller.CarController()
        }
    def disconnect(self, client):
        print('client disconnected: %s:%s' % client.addr)
        del self.clients[client.ID]
    def message(self, client, data):
        print('message from %s:%s: %s' % (client.addr[0], client.addr[1], data))
        self.clients[client.ID]['controller'].accept_data(data)
    
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
            print('error number %i' % e.errno)
            if e.errno == 10048:
                print('- Port %i unavailable' % port)
            else:
                print('Fatal: Failed to initialize server: %s' % e)
                return
    if not server:
        print('Fatal: Could not find any open ports between %i and %i' % PORTS)
        return
    server.add_dispatcher(Dispatcher())
    try:
        main_server(server)
    finally:
        server.socket.close()

if __name__ == '__main__':
    main()
