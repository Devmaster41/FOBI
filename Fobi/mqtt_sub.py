import paho.mqtt.client as mqtt
import time
import os
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *


# Control table address
ADDR_MX_TORQUE_ENABLE      = 24
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36

# Protocol version
PROTOCOL_VERSION            = 1.0

# Default setting
#DXL_ID                      = 4
BAUDRATE                    = 57600
DEVICENAME                  = "/dev/ttyUSB0"


TORQUE_ENABLE               = 1
TORQUE_DISABLE              = 0
DXL_MINIMUM_POSITION_VALUE  = 600
DXL_MAXIMUM_POSITION_VALUE  = 600
DXL_MOVING_STATUS_THRESHOLD = 20
#dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]

portHandler = PortHandler(DEVICENAME)

packetHandler = PacketHandler(PROTOCOL_VERSION)

# Open port

if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

def set_Angle(ID,min,max):
    packetHandler.write2ByteTxRx(portHandler, ID, 6, min)
    packetHandler.write2ByteTxRx(portHandler, ID, 8, max)

def Fobi_setAngle():
    set_Angle(2,368,652)
    set_Angle(3,510,635)

def Fobi_TurnRight():

    Goal_position(2,30)

def Fobi_TurnLeft():
    Goal_position(2,360)

def Fobi_TurnDown():
    Goal_position(3,635)

def Fobi_TurnUp():
    Goal_position(3, 515)

def Fobi_defualt():
    Goal_position(2,512)
    Goal_position(3,555)

def set_Speed(ID,Speed):
    packetHandler.write1ByteTxRx(portHandler,ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    packetHandler.write1ByteTxOnly(portHandler,ID, 26, 0)
    packetHandler.write1ByteTxOnly(portHandler,ID, 27, 0)
    packetHandler.write1ByteTxOnly(portHandler,ID, 28, 32)
    packetHandler.write1ByteTxOnly(portHandler,ID, 29, 32)
    packetHandler.write2ByteTxRx(portHandler, ID, 32, Speed)

def Goal_position(ID,position):
    packetHandler.write2ByteTxRx(portHandler, ID, 30, position)

def on_connect(client,userdata,flags,rc):
    print("connected with code :"+str(rc))
    client.subscribe("backend/eyes/face/x")
    client.subscribe("backend/eyes/face/y")
    client.subscribe("module/motor/request")
    client.subscribe("fobi/set")
def Xturn(px):
    #set_Speed(2,50)
    a,b,c = packetHandler.read2ByteTxRx(portHandler,2,36)
    err = int((px-160)*(62/320))
    err = int(-err*3.41)
    #print(err)
    out = (a+err)
    Goal_position(2,out)

def Yturn(py):
    #set_Speed(3,50)
    a,b,c = packetHandler.read2ByteTxRx(portHandler,3,36)
    #print(a)
    err = int((120-py)*(49/240))
    err = int(err*3.41)
    #print(a)
    out = (a-err)
    Goal_position(3,out)
#set_Speed(2,50)
#set_Speed(3,50)
def on_message(client,userdata,msg):

    packetHandler.write1ByteTxRx(portHandler, 2, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    packetHandler.write1ByteTxRx(portHandler, 3, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    Fobi_setAngle()
    message = msg.payload.decode('utf-8')
    if msg.topic == "module/eyes/face/x":
        x = int(message)
        message = msg.payload.decode('utf-8')
        print(x)
        Xturn(x)
        #Fobi_defualt()

    elif msg.topic == "module/eyes/face/y":
        y = int(message)
        print(y)
        #Fobi_defualt()
        Yturn(y)
    elif msg.topic == "fobi/set" :
        Fobi_defualt()
        print("set")
    elif msg.topic == "module/motor/request":
        if message == "1":
            Fobi_TurnUp()
        elif message == "2":
            Fobi_TurnDown()
        elif message == "3":
            Fobi_TurnLeft()
        elif message == "4":
            Fobi_TurnRight()
        else:
            Fobi_defualt()
set_Speed(2,30)
set_Speed(3,30)
client = mqtt.Client()
client.username_pw_set("username",password="hcilab")
client.on_connect = on_connect
client.on_message = on_message


client.connect("localhost",1883,60)
client.loop_forever()
client.disconnect()

portHandler.closePort()
