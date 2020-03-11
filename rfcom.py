#!/usr/bin/env python3
"""PyBluez simple example rfcomm-client.py
Simple demonstration of a client application that uses RFCOMM sockets intended
for use with rfcomm-server.
Author: Albert Huang <albert@csail.mit.edu>
$Id: rfcomm-client.py 424 2006-08-24 03:35:54Z albert $
"""

import sys

import bluetooth


addr = 'ESP32test'

# if len(sys.argv) < 2:
#     print("No device specified. Searching all nearby bluetooth devices for "
#           "the SampleServer service...")
# else:
#     addr = sys.argv[1]
#     print("Searching for SampleServer on {}...".format(addr))

# search for the SampleServer service
host = "24:6F:28:B5:1A:3A"
service_matches = bluetooth.find_service(address=host,name=b'ESP32SPP\x00')
# service_matches = bluetooth.find_service(address=host)
print(service_matches)
if len(service_matches) == 0:
    print("Couldn't find the SampleServer service.")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("Connecting to \"{}\" on {}".format(name, host))

# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))
sock.settimeout(10)
# sock.listen(1)
# client_socket,address = sock.accept()
data = sock.recv(1024)
print(data)
# client_socket.close()
sock.close()
# print("Connected. Type something...")
# sock.settimeout(2)
# response = ""
# try:
#     while True:
#         r = sock.recv(255)
#         if not r:
#             break

#         response = response + r
#         if r.find(";") != -1: # we have reach end of message
#             break
# except:
#     pass
# print("Response: (%s)" % response)

# sock.close()