#!/usr/bin/python

import SocketServer
import struct
import time
import sys
from math import *

M_PI =  3.1415926535897932385

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
        print "%s wrote:" % self.client_address[0]
        print repr(self.data), len(self.data)
        data = struct.unpack("3iIi", self.data)
        print time.time()
        print data
        
        ra = data[3]*(M_PI/0x80000000)
        dec = data[4]*(M_PI/0x80000000)
        cdec = cos(dec)

        desired_pos = []
        desired_pos.append(cos(ra)*cdec)
        desired_pos.append(sin(ra)*cdec)
        desired_pos.append(sin(dec))

        print desired_pos
        
        #just send back the same data, but upper-cased
        reply = struct.pack("3iIii", 24, 0, time.time(), data[3], data[4], 0)
        print repr(reply)
        self.request.send(reply)
        self.request.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 10001

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.allow_reuse_address = True
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
