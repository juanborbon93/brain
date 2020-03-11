# Imports
import time
import serial

# Serial port parameters
serial_speed = 115200
serial_port = 'COM7'

# Test with USB-Serial connection
# serial_port = '/dev/tty.usbmodem1421'

ser = serial.Serial(serial_port, serial_speed, timeout=2)
n=0
while n<10:
    msg = ser.readline().decode('utf-8')
    print(msg)
    n+=1

