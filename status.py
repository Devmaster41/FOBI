import time
import board
import neopixel
import paho.mqtt.client as mqtt


R = [0,0,255,0]
G = [0,255,0,0]
B = [0,0,0,255]


pixel_pin = board.D21
num_pixels = 16
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)
def LED(a):
    pixels.fill((R[int(a)], G[int(a)], B[int(a)]))
    pixels.show()
    print(R[int(a)], G[int(a)], B[int(a)])
    time.sleep(2)
      
def on_connect(client,userdata,flags,rc):
    print("connected with code :"+str(rc))
    client.subscribe("status")

def on_message(client,userdata,msg):
    message = msg.payload.decode('utf-8')
    if msg.topic == "status":
        print(message)
        LED(message)
        
    
client = mqtt.Client()
client.username_pw_set("username",password="hcilab")
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost")
client.loop_forever()
client.disconnect()

