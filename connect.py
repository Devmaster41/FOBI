import os
import paho.mqtt.client as mqtt

def on_connect(client,userdata,flags,rc):
    client.subscribe("module/camera/request")

def on_message(client,userdata,msg):
    message = msg.payload.decode('utf-8')
    if msg.topic == "module/camera/request":
        cmd = "python ther_pnter.py"
        os.system(cmd)
    


client = mqtt.Client()
client.username_pw_set("username",password="hcilab")
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.137.188",1883,60)
client.loop_forever()
client.disconnect()
