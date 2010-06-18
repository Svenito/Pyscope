#!/usr/bin/env python
# -*- coding: utf-8 -*-
import struct
import time
import socket, select
from math import *

M_PI =  3.1415926535897932385

# List of socket objects that are currently open
open_sockets = []

# AF_INET means IPv4.
# SOCK_STREAM means a TCP connection.
# SOCK_DGRAM would mean an UDP "connection".
listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
# Allow reuse of socket if socket is idle
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

listening_socket.bind( ("", 10001) )
listening_socket.setblocking(0)
listening_socket.listen(5)

current_position = []

def printit(ra_int, dec_int):
    h = ra_int
    d = floor(0.5 + dec_int*(360*3600*1000/4294967296.0));
    dec_sign = ''
    if d >= 0:
        if d > 90*3600*1000:
            d =  180*3600*1000 - d;
            h += 0x80000000;
        dec_sign = '+';
    else:
        if d < -90*3600*1000:
            d = -180*3600*1000 - d;
            h += 0x80000000;
        d = -d;
        dec_sign = '-';
    
    
    h = floor(0.5+h*(24*3600*10000/4294967296.0));
    ra_ms = h % 10000; h /= 10000;
    ra_s = h % 60; h /= 60;
    ra_m = h % 60; h /= 60;
    
    h %= 24;
    dec_ms = d % 1000; d /= 1000;
    dec_s = d % 60; d /= 60;
    dec_m = d % 60; d /= 60;

    print "ra =", h,"h", ra_m,"m",ra_s,".",ra_ms
    print "dec =",dec_sign, d,"d", dec_m,"m",dec_s,".",dec_ms

data = [0, 0, 0, 0, 0]
while True:
    # Waits for I/O being available for reading from any socket object.
    rlist, wlist, xlist = select.select( [listening_socket] + open_sockets, 
                                         [listening_socket] + open_sockets, [])
    for i in rlist:
        if i is listening_socket:
            new_socket, addr = listening_socket.accept()
            open_sockets.append(new_socket)
        else:
            data = i.recv(1024)
            if data == "":
                open_sockets.remove(i)
                print "Connection closed"
            else:
                data = struct.unpack("3iIi", data)
                ra = data[3]*(M_PI/0x80000000)
                dec = data[4]*(M_PI/0x80000000)
                cdec = cos(dec)

                desired_pos = []
                desired_pos.append(cos(ra)*cdec)
                desired_pos.append(sin(ra)*cdec)
                desired_pos.append(sin(dec))
                printit(data[3], data[4])
                
                #Set desired position and get current
                #send current position back to client
                #update current position
                
                print
    for w in wlist:
        if not w is listening_socket:
            reply = struct.pack("3iIii", 24, 0, time.time(), data[3], data[4], 0)
            wlist[0].send(reply)

    time.sleep(1)
