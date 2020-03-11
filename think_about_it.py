import serial
import time
import argparse
import random
import numpy as np
from multiprocessing import Process, Queue, Array

#set up parser commands
parser = argparse.ArgumentParser(description='testing stuff')
parser.add_argument('-p1','--duino',help='arduino COM port',required = True)
parser.add_argument('-p2','--grbl',help='grbl COM port',required = True)
parser.add_argument('-rst','--reset',help='reset machine mid job',required = False)
args = parser.parse_args()

print("duino port: %s" % args.duino)
print("grbl port: %s" % args.grbl)
print(args.reset)

# signals that we get from the sensors
signal = "delta"
keys = ("signal strength","attention","meditation",
        "delta","theta","low alpha","high alpha",
        "low beta","high beta","low gamma","high gamma")
freq_range = [0.1,10]
amplitudes = 15
speed_mult = 3
z_advance = 0.1*speed_mult
xy_advance = -0.003*speed_mult
xpos = 0
ypos = 0
zpos = 0
max_xy = -330
t = 0
axis_mult = [1,1,1]
brain_active = [True,True]


#set up the serial connections
s1 = serial.Serial(args.duino,9600)
s2 = serial.Serial(args.grbl,115200)
print('opening serial port')

#wake up grbl
s2.write(str.encode("\r\n\r\n"))
time.sleep(2)
s2.flushInput()
s2.write(str.encode("G92 X0 Y0 Z0")) 

# define our brains
class Brain:
    def __init__(self):
        self.amplitude = 0
        self.values = [0]
        self.mean = 0
        self.std = 1
        self.normal = 0
        self.active = False
        
    def update(self,new_val):
        new_val = (float)(new_val)
        if len(self.values) > 20:
            self.values.pop(0)
        self.values.append(new_val)
        self.mean = np.mean(self.values)
        self.std = np.std(self.values)
        self.normal = (self.values[-1]-np.min(self.values))/(np.max(self.values)-np.min(self.values))
        self.amplitude = self.normal*amplitudes
##        print('latest:',self.values[-1],
##              ' min:',np.min(self.values),
##              ' max:',np.max(self.values),
##              ' norm:',self.normal,
##              ' amp:',self.amplitude)
##        print('normalized in',self.normal)
    

def get_signal(A):
    global brain_active,A1,A2
    brain1 = Brain()
    brain2 = Brain()
    while True:
        msg = s1.readline().decode('utf-8')
        msg = (str)(msg)#[:-2]

        msg = msg.split(',')
        if len(msg) == 22:
            b1 = dict(zip(keys,msg[:11]))
            b2 = dict(zip(keys,msg[11:]))
            brain_signals = [b1[signal],b2[signal]]
            brain1.active = not b1["signal strength"] == '200'
            brain2.active = not b2["signal strength"] == '200'
##            print(not b1["signal strength"] == '200',not b2["signal strength"] == '200')
            brain1.update(brain_signals[0])
            brain2.update(brain_signals[1])
            A1 = brain1.amplitude*(not b1["signal strength"] == '200')
            A2 = brain2.amplitude*(not b2["signal strength"] == '200')
##            print('amps',A1,A2)
            if A.full():
                A.get()
            A.put([A1,A2,
                   not b1["signal strength"] == '200',
                   not b2["signal strength"] == '200'])

rads = np.linspace(0,2*np.pi,20)
def grbl(A):
    global xpos,ypos,zpos,brain1,brain2
    F = 400
    if args.reset == None:
        xymean = -1.2*amplitudes
    else:
        xymean = 0
    while xymean>max_xy:
##        A1 = np.random.random()*amplitudes
##        A2 = np.random.random()*amplitudes
        amps = A.get()
##        print('active',amps[2],amps[3])
        A1 = amps[0]
        A2 = amps[1]
##        A1 = brain1.normal*amplitudes#*brain_active[0]
##        A2 = brain2.normal*amplitudes#*brain_active[1]
##        print('normalized out',brain1.normal,brain2.normal)
##        print('AMPLITUDES',A1,A2)
        s2.write('?\n')
        grbl_status = s2.readline().decode('utf-8')
        grbl_status = grbl_status[1:-3].split(b',')
        if len(grbl_status)==3:
            print(grbl_status)
            buffer = (int)(grbl_status[1].split(':')[-1])
            print('buffer: ',buffer)
        if buffer < 13 and (A1+A2)>2:
            F = max(800*((A1+A2)/2)/amplitudes,30)
            for i in rads:
                xpos= xymean+A1*np.sin(i)
                ypos= xymean+A2*np.sin(i)
                xymean += xy_advance
                zpos += z_advance
                msg = 'G1 X{} Y{} Z{} F{}'.format(xpos,ypos,zpos,F)
                print(msg)
                s2.write(str.encode(msg+'\n'))
                grbl_out = s2.readline().decode('utf-8')
                time.sleep(0.5)
    

if __name__ == '__main__':
    s2.write(str.encode("\r\n\r\n"))
    time.sleep(2)
    s2.flushInput()
    s2.write(str.encode("G92 X0 Y0 Z0"))
    
    A = Queue(1)
    update_signal = Process(target=get_signal,args = (A,))
    update_grbl = Process(target=grbl,args = (A,))

    update_signal.start()
    update_grbl.start()
    update_signal.join()
    update_grbl.join()

    

    
