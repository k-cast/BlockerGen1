#!/usr/bin/python
import serial
import time

## Pump fill configuration: ##

tipvolume = 100 #how much you want to fill the tip here in ul

dispensevolume = 1.5 #how much you want to dispense per pump dispense command here in ul

stepsul = 192 #steps/ul 
fv = bytes(str(stepsul*tipvolume), 'ascii') #actual steps to fill the tip used in the filling def converted to str for command
dv = bytes(str(stepsul*dispensevolume), 'ascii') #acutal dispense steps converted to str for command

## Robot configuration ##

xfeed = 10000
yfeed = 10000
zfeed = 2000

# This is the position in the back left corner of the nest #
xoffset = -61.9
yoffset = -171.15
zoffset = -20.8

## Convert robot config to bytes ##
xoffset = bytes(str(xoffset), 'ascii')
yoffset = bytes(str(yoffset), 'ascii')
zoffset = bytes(str(zoffset), 'ascii')

xfeed = bytes(str(xfeed), 'ascii')
yfeed = bytes(str(yfeed), 'ascii')
zfeed = bytes(str(zfeed), 'ascii')

## Open serial ports ##
robot = serial.Serial('/dev/ttyACM0',115200)
pump = serial.Serial('/dev/ttyUSB0' , 9600)
print('opening Serial Ports')
 
## Open g-code file (only place one gcode file each gcode folder on the desktop) ##
#g1file = open('/home/pi/Desktop/gcode1/gcode1.gcode','r')
g2file = open('/home/pi/Desktop/gcode2/gcode2.gcode','r')
print('opening gcode files')

## cleanup gcode strings ##
def removeComment(string):
    if (string.find(';')==-1):
        return string
    else:
        return string[:string.index(';')]

## this function is used to wait for move to complete ##
def robotwait():
    robot.flush()
    while True:
        robot_out = str(robot.readline()) #wait for response
        print(' robot: ' + robot_out.strip())
        if robot_out[2] == 'Z': #get an Z_move_comp response
            break

## wait to send next command to not crash the pump contoller ##
def pumpwait():
    pump.flush()
    while True:
        time.sleep(.5)
        pump.flushOutput()
        pump.write(b'/1?\r\n')  #query the pump's position
        pump_out = str(pump.readline()) #wait for response
        print(' pump: ' + pump_out.strip())
        if pump_out[8] == '`': #get a done moving response from the pump
            time.sleep(1)
            break
             
## for use in motion functions, enter x position and feedrate (default will be used if no value provided) ##
def xmove(xm, xf):
    xm = bytes(str(xm), 'ascii')
    xf = bytes(str(xf), 'ascii')
    robot.write(b'G1 X' + xm + b' ' + xf + b' ;\r\n')
    robotwait()

## for use in motion functions, enter y position and feedrate (default will be used if no value provided) ##
def ymove(ym, yf):
    ym = bytes(str(ym), 'ascii')
    yf = bytes(str(yf), 'ascii')
    robot.write(b'G1 Y' + ym + b' F' + yf + b' ;\r\n')
    robotwait()

## for use in motion functions, enter x and y positions and feedrate (default will be used if no value provided) ##
def xymove(xxym, xyym, xf):
    xxym = bytes(str(xxym), 'ascii')
    xyym = bytes(str(xyym), 'ascii')
    xf = bytes(str(xf), 'ascii')
    robot.write(b'G1 X' + xxym + b' Y' + xyym + b' F' + xf + b' ;\r\n')
    robotwait()
    
## for use in motion functions, enter z position and feedrate (default will be used if no value provided) ##
def zmove(zm, zf):
    zm = bytes(str(zm), 'ascii')
    zf = bytes(str(zf), 'ascii')
    robot.write(b'G1 Z' + zm + b' F' + zf + b' ;\r\n')
    robotwait()

## Home/initialize function ##
def initialize():
    
    #wake up pump
    pump.write(b'\r\n\r\n') #don't know if the pump sleeps
    time.sleep(1)
    pump.flushInput()
    pump.write(b'/1ZR\r\n') #initialize pump 1
    pump.write(b'/2ZR\r\n') #initialize pump 2
    print('initializing the pump')


    # Wake up robot
    print('initializing robot')
    robot.write(b'\r\n\r\n') # Hit enter a few times to wake the controller
    time.sleep(1)   # Wait for controller to wake up
    robot.flushInput()  # Flush startup text in serial input
    robot.write(b'M203 X' + xfeed + b' Y' + yfeed + b' Z' + zfeed  + b' ;\r\n') #set feedrates
    zmove(80, 2000)
    robot.write(b'G28 ;\r\n') #home the XYZ robot
    robotwait()
    robot.write(b'G54 ;\r\n') #switch to workspace 1
    robot.write(b'G92 X' + xoffset + b' Y' + yoffset + b' Z' + zoffset + b' ;\r\n') #Zero to offset position
    zmove(80, 2000)
    ymove(70, 3000)
    
## dispense paths that will be used in a pattern ##
def dispensepath1():
    # Stream g-code
    g1file = open('/home/pi/Desktop/gcode1/gcodeblocker.gcode','r') #open and read gcode file
    pump.write(b'/1S15D4400R\r\n') #dispense pump 1
    time.sleep(.1)
    pump.write(b'/2S15D4400R\r\n')
    for line in g1file:
        l = line
        l = l.strip() # Strip all EOL characters for streaming
        if  (l.isspace()==False and len(l)>0) :
            print('Sending: ' + l)
            robot.write(bytes(l, 'ascii') + b'\n') # Send g-code block
            if l[1] == '1':
                robotwait()

def dispensepath2():
    # Stream g-code
    for line in g2file:
        l = line
        l = l.strip() # Strip all EOL characters for streaming
        if  (l.isspace()==False and len(l)>0) :
            print('Sending: ' + l)
            robot.write(bytes(l, 'ascii') + b'\n') # Send g-code block
            robot_out = str(robot.readline()) # Wait for response with carriage return
            print(' robot: ' + robot_out.strip())

## Fill the system tubing etc. with fluid ##
def sysprime():
    pump.write(b'/1W4A40000OA0IA40000OA0IA40000OA0IM2000A9600OA0IR\r\n') #re-init
    pumpwait()

## the tip filling process ##
def fill():
    print('filling...')
    zmove(80, 2000)     
    xymove(44, 53.2, 5000) #this is just an example position where the vials will be
    zmove(15, 1000) #move tips down into vials
    zmove(2, 500) #slow move to bottom
    pump.write(b'/2S1A24000D400R\r\n') #fill tip and dispense 400 steps
    time.sleep(.1)
    pump.write(b'/1S1A24000D400R\r\n') #fill second tip
    time.sleep(5)
    zmove(80, 2000) #move Z up
    #xmove(13, 2000) #move to second tip
    #zmove(15, 1000)
    #zmove(2, 500)
    #pump.write(b'/1S1A24000D400R\r\n') #fill second tip
    #time.sleep(5)
    zmove(80, 2000)

## Empyting the tips ##
def empty():
    print('emptying...')
    zmove(80, 1000)        
    xymove(44, 53.2, 5000) #this is just an example position where the vials will be
    zmove(60, 1000) #move tips down into vials
    pump.write(b'/1S1A0R\r\n') #empty syringe 1
    pump.write(b'/2S1A0R\r\n') #empty syringe 2
    time.sleep(5) #wait just in case
    zmove(80, 2000) #move Z up
    ymove(70, 1000)

## Move the tip to the back left corner of the nest to check calibration ##
def origin():
    zmove(100, 1000)
    xymove(0, 0, 1000)
    zmove(10, 1000)
    zmove(0, 500)
    
##pre-run prime, used to get air pocket out of tips
def tipprime():
    zmove(50, 1000)
    xymove(97, 17.2, 5000)
    zmove(33, 1000)
    pump.write(b'/1D800R\r\n')
    time.sleep(1)
    ymove(15, 500)
    zmove(50, 1000)

## run babalu chips ##
def babalu():
    print('running babalu tray')
    zmove(50, 1000) #move Z up just in case
    tipprime()
    xymove(59.14, -145.5, 5000) #move to the start of the first spot
    zmove(5, 2000) #rapid move
    zmove(-.5, 500) #move down to the first spot
    for i in range(3):
        robot.write(b'G55 ;\r\n') #set position coordinate system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        robot.write(b'G92 X0 Y0 Z0 ;\r\n') #zeros system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        dispensepath1()
        time.sleep(.5)
        zmove(10, 1000) #move up
        if i < 2:
            xymove(0, 49.53, 2000) #move back to the next spot
        if i < 2:
            zmove(0, 500)
    robot.write(b'G54 ;\r\n') #back to cord system 1
    robot_out = str(robot.readline()) # Wait for response with carriage return
    print(' robot: ' + robot_out.strip())
    zmove(50, 1000) #move up
    ymove(40, 3000)

## run falcon ##
def falcon():
    print('running babalu tray')
    zmove(50, 1000) #move Z up just in case
    tipprime()
    xymove(75.86, -145.7, 5000) #move to the start of the first spot
    zmove(5, 2000) #rapid move
    zmove(-.5, 500) #move down to the first spot
    for i in range(3):
        robot.write(b'G55 ;\r\n') #set position coordinate system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        robot.write(b'G92 X0 Y0 Z0 ;\r\n') #zeros system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        dispensepath1()
        time.sleep(.5)
        zmove(10, 1000) #move up
        if i < 2:
            xymove(0, 49.53, 2000) #move back to the next spot
        if i < 2:
            zmove(0, 500)
    robot.write(b'G54 ;\r\n') #back to cord system 1
    robot_out = str(robot.readline()) # Wait for response with carriage return
    print(' robot: ' + robot_out.strip())
    zmove(50, 1000) #move up
    ymove(40, 3000)

## run cardea carrier##
def cardea():
    print('running cardea tray')
    fill()
    zmove(80, 1000) #move Z up just in case
    xymove(17.5, -135.2, 5000) #move to the start of the first spot
    zmove(5, 2000) #rapid move
    zmove(-2.2, 500) #move down to the first spot
    for i in range(5):
        robot.write(b'G55 ;\r\n') #set position coordinate system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        robot.write(b'G92 X0 Y0 Z0 ;\r\n') #zeros system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        dispensepath1()
        time.sleep(.5)
        zmove(10, 1000) #move up
        if i < 4:
            xymove(0, 28.58, 2000) #move back to the next spot
        if i < 4:
            zmove(0, 500)
    robot.write(b'G54 ;\r\n') #back to cord system 1
    robot_out = str(robot.readline()) # Wait for response with carriage return
    print(' robot: ' + robot_out.strip())
    zmove(80, 1000) #move up
    ymove(70, 3000)

## run cardea carrier##
def gaia():
    print('running cardea tray')
    zmove(50, 1000) #move Z up just in case
    tipprime()
    xymove(27.42, -140.6, 5000) #move to the start of the first spot
    zmove(5, 2000) #rapid move
    zmove(-.5, 500) #move down to the first spot
    for i in range(5):
        robot.write(b'G55 ;\r\n') #set position coordinate system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        robot.write(b'G92 X0 Y0 Z0 ;\r\n') #zeros system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        dispensepath1()
        time.sleep(.5)
        zmove(10, 1000) #move up
        if i < 4:
            xymove(0, 28.58, 2000) #move back to the next spot
        if i < 4:
            zmove(0, 500)
    robot.write(b'G54 ;\r\n') #back to cord system 1
    xymove(93.95, -140.6, 5000) #move to the start of the first spot
    zmove(5, 2000) #rapid move
    zmove(-1.6, 500) #move down to the first spot
    for i in range(5):
        robot.write(b'G55 ;\r\n') #set position coordinate system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        robot.write(b'G92 X0 Y0 Z0 ;\r\n') #zeros system
        robot_out = str(robot.readline()) # Wait for response with carriage return
        print(' robot: ' + robot_out.strip())
        dispensepath1()
        time.sleep(.5)
        zmove(10, 1000) #move up
        if i < 4:
            xymove(0, 28.58, 2000) #move back to the next spot
        if i < 4:
            zmove(0, 500)
    robot.write(b'G54 ;\r\n') #back to cord system 1
    robot_out = str(robot.readline()) # Wait for response with carriage return
    print(' robot: ' + robot_out.strip())
    zmove(50, 1000) #move up
    ymove(40, 3000)

## Terminal loop to use inplace of gui ##
#while True: 
#   inputchar = str(input())
#   if inputchar == 'i': #type 'i' in console to initialize
#       initialize()
#   elif inputchar == 'f': #type 'f' in console to fill [note this will probably change depending on the reservior arrangement]
#        fill()
#   elif inputchar == 'r1': #type 'r1' to run tray 1
#       babalu()
#   elif inputchar == 'r2': #type 'r2'
#        cardea()
#   elif inputchar == 'e': #type 'e' to empty the tips
#        empty()


#Close file and serial port [saving in case I decide to use these later for shutdown or something]
#gfile.close()
#robot.close()
#pump.close()
