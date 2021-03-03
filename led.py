import time
import board
import neopixel
import os
import paho.mqtt.client as mqtt
import threading

res = ""
sub_txt = ""
STATE = "result"
ST = "null"

R = [0,255,255,255,0,0,120,255,255,0]
G = [0,255,0,106,0,255,0,0,255,255]
B = [0,255,0,0,255,0,255,212,0,255]


_color = []

pixel_pin = board.D21
num_pixels = 24
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)
def LED(a):
    global ST
    if a != "เปิดไฟ" and a!="": 
        a = int(a)
        ST = "not null"
        pixels.fill((R[a], G[a], B[a]))
        print(R[a], G[a], B[a])
        pixels.show()
        time.sleep(2)
    elif a!= "เปิดไฟ" and a == "" and ST == "null":
        pixels.fill((255, 255, 255))
        pixels.show()
        

def _connectLED():
    global res , sub_txt , STATE,ST
    while True:
        if res.split(",")[0] == "เปิดไฟ":
            sub_txt = res
            if STATE == "result":
                STATE = "not result"
                ST = "null"
                cmd = "mosquitto_pub -h 192.168.137.188 -u username -P hcilab -t module/talking/result -m 1"
                os.system(cmd)
    
            for a in sub_txt.split(","):
                if res.split(",")[0] != "เปิดไฟ" or res != sub_txt:
                    STATE = "result"
                    break
                LED(a)
        elif res.split(",")[0] == "ปิดไฟ":
            LED(0)
            cmd = "mosquitto_pub -h 192.168.137.188 -u username -P hcilab -t module/talking/result -m 1"
            os.system(cmd)
            STATE = "result"

        
      
def on_connect(client,userdata,flags,rc):
    print("connected with code :"+str(rc))
    client.subscribe("module/led/request")

def on_message(client,userdata,msg):
    message = msg.payload.decode('utf-8')
    if msg.topic == "module/led/request":
        global res
        res = message
    
 
def _mqtt():
    client = mqtt.Client()
    client.username_pw_set("username",password="hcilab")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.137.188",1883,60)
    client.loop_forever()
    client.disconnect()

if __name__=="__main__":
    MQTTs = threading.Thread(target=_mqtt)
    connectLED = threading.Thread(target=_connectLED)
    MQTTs.start()
    connectLED.start()
