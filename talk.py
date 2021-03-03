import time
import os
import paho.mqtt.client as mqtt
import threading

def subtxt(x):
    time.sleep(1)
    cmd = "play {}".format("./"+x.split(",")[0]+"/"+x.split(",")[1]+".mp3")
    os.system(cmd)
    cmd = "mosquitto_pub -u username -P hcilab -t module/talking/result -m 1"
    os.system(cmd)
    
            

def on_connect(client,userdata,flags,rc):
    print("connected with code :"+str(rc))
    client.subscribe("module/talking/id")


def on_message(client,userdata,msg):
    message = msg.payload.decode('utf-8')
    if msg.topic == "module/talking/id":
        cmd = "mosquitto_pub -u username -P hcilab -t status -m 3"
        os.system(cmd)
        subtxt(str(message))
        
client = mqtt.Client()
client.username_pw_set("username",password="hcilab")
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost",1883,60)
client.loop_forever()
client.disconnect()
