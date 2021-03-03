import cv2
import numpy as np
import paho.mqtt.client as mqtt


broker = "localhost"
username = "username"
password = "hcilab"

client = mqtt.Client()
client.username_pw_set(username,password)
client.connect(broker)

cap = cv2.VideoCapture(0)
faces_cascade = cv2.CascadeClassifier('Fobi/haarcascade_frontalface_alt2.xml')

cap.set(3,320)
cap.set(4,240)

Face_status = False
Skin_status = False
X = 0
Y = 0
o_x = 0
o_y = 0
o_w = 0
o_h = 0

while True:

    Face_status = False
    Skin_status = False
    ret,frame = cap.read()
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    faces = faces_cascade.detectMultiScale(frame,1.3,5)
    for x,y,w,h in faces:
        X = int(x+(w/2))
        Y = int(y+(h/2))
        Face_status = True
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,189,0),2)


    if not Face_status:
        lower_blue = np.array([0,61,0])
        upper_blue = np.array([57,255,217])


        mask = cv2.inRange(hsv,lower_blue,upper_blue)
        _,contours,_ = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

        for c in contours:
            if cv2.contourArea(c) <=500 :
                continue
            x,y,w,h = cv2.boundingRect(c)
            Skin_status = True
            X = int(x+(w/2))
            Y = int(y+(h/2))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 188,255), 1)
            if w+h > o_w+o_h:
                cv2.drawContours(frame,contours,-1,(0,255,0),3)

            o_x,o_y,o_w,o_h = x,y,w,h
    print("face ",Face_status)
    print("skin ",Skin_status)
    cv2.imshow("frame",frame)
    #cv2.imshow('mask',mask)

    if cv2.waitKey(1) == 27:
        break

    if Face_status or Skin_status:
        client.publish("module/eyes/skin/see","1")

        client.publish("backend/eyes/face/x", str(X))
        print("x = ",X)
        client.publish("backend/eyes/face/y", str(Y))
        print("Y = ",Y)
    else:
        client.publish("module/eyes/skin/see","0")
    Face_status = False
    Skin_status = False
cap.release()
cv2.destroyAllWindows()
client.disconnect()
