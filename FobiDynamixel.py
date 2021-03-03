
import os
import paho.mqtt.client as mqtt
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

from dynamixel_sdk import *                    # Uses Dynamixel SDK library

# Control table address
ADDR_MX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                      = 2                 # Dynamixel ID : 1
BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
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
def set_Speed(ID,Speed):
    packetHandler.write1ByteTxOnly(portHandler,ID, 26, 0)
    packetHandler.write1ByteTxOnly(portHandler,ID, 27, 0)
    packetHandler.write1ByteTxOnly(portHandler,ID, 28, 32)
    packetHandler.write1ByteTxOnly(portHandler,ID, 29, 32)
    packetHandler.write2ByteTxRx(portHandler, ID, 32, Speed)
def set_Angle(ID,min,max):
    packetHandler.write2ByteTxRx(portHandler, ID, 6, min)
    packetHandler.write2ByteTxRx(portHandler, ID, 8, max)
def Goal_position(ID,position):
    packetHandler.write2ByteTxRx(portHandler, ID, 30, position)

packetHandler.write1ByteTxRx(portHandler,2, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
packetHandler.write1ByteTxRx(portHandler,3, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)

id_2_minAngle = 312
id_2_maxAngle = 712
id_3_minAngle = 500
id_3_maxAngle = 700

def Fobi_config():
    set_Speed(2,30)
    set_Angle(2,id_2_minAngle,id_2_maxAngle)

    set_Speed(3,30)
    set_Angle(3,id_3_minAngle,id_3_maxAngle)
def Fobi_TurnLeft():
    Goal_position(2, id_2_maxAngle)
def Fobi_TurnRight():
    Goal_position(2,id_2_minAngle)
def Fobi_TurnUp():
    Goal_position(3,id_3_minAngle)
def Fobi_TurnDown():
    Goal_position(3,id_2_maxAngle)
def Fobi_Center():
    Goal_position(2,512)
    Goal_position(3,600)
Fobi_config()
def on_connect(client,userdata,flags,rc):
    print("connected "+str(rc))
    client.subscribe("module/motor/rotate")
    client.subscribe("module/motor/speed/2")
    client.subscribe("module/motor/speed/3")
    client.subscribe("module/motor/angle/2/min")
    client.subscribe("module/motor/angle/2/max")
    client.subscribe("module/motor/angle/3/min")
    client.subscribe("module/motor/angle/3/max")
def on_message(client,userdata,msg):
    message = msg.payload.decode("utf-8")
    print(message)

    if msg.topic == "module/motor/rotate":
        if message == "left":
            Fobi_TurnLeft()
        if message == "right":
            Fobi_TurnRight()
        if  message == "up":
            Fobi_TurnUp()
        if  message == "down":
            Fobi_TurnDown()
        if message == "center":
            Fobi_Center()
        if  message == "disableX":
              packetHandler.write1ByteTxRx(portHandler,2, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
        if  message == "disableY":
              packetHandler.write1ByteTxRx(portHandler,3, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
    elif msg.topic == "module/motor/speed/2":
        set_Speed(2,int(message))
    elif msg.topic == "module/motor/speed/3":
        set_Speed(3,int(message))
    elif msg.topic == "module/motor/angle/2/min":
        id_2_minAngle = int(message)
        set_Angle(2,id_2_minAngle,id_2_maxAngle)
    elif msg.topic == "module/motor/angle/2/min":
        id_2_maxAngle = int(message)
        set_Angle(2,id_2_minAngle,id_2_maxAngle)
    elif msg.topic == "module/motor/angle/2/min":
        id_3_minAngle = int(message)
        set_Angle(2,id_3_minAngle,id_3_maxAngle)
    elif msg.topic == "module/motor/angle/2/min":
        id_3_maxAngle = int(message)
        set_Angle(2,id_3_minAngle,id_3_maxAngle)
client = mqtt.Client()
client.username_pw_set("username",password="hcilab")
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost")
client.loop_forever()
client.disconnect()
# Close port
portHandler.closePort()
