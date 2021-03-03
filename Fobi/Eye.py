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
faces_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
#cv2.namedWindow("Trackbars")
cap.set(3,320)
cap.set(4,240)
#cv2.createTrackbar("L - H","Trackbars",0,255,nothing)
#cv2.createTrackbar("L - S","Trackbars",0,255,nothing)
#cv2.createTrackbar("L - V","Trackbars",0,255,nothing)
#cv2.createTrackbar("U - H","Trackbars",0,255,nothing)
##cv2.createTrackbar("U - S","Trackbars",0,255,nothing)
#cv2.createTrackbar("U - V","Trackbars",0,255,nothing)
Face_status = False
Skin_status = False
X = 0
Y = 0
old_X = 0
old_Y = 0
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
        client.publish("face", "helllo face")
    #l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    #l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    #l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    #u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    #u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    #u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower_blue = np.array([0,55,169])
    upper_blue = np.array([51,168,249])


    mask = cv2.inRange(hsv,lower_blue,upper_blue)
    _,contours,_ = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(frame,contours,-1,(0,255,0),3)
    for c in contours:
        Skin_status = True
        if cv2.contourArea(c) <= 500 :
            continue
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 188,255), 1)
        center = (x,y)
        #print (center)
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) == 27:
        break
    if Face_status or Skin_status:
        client.publish("module/eyes/skin/see","1")
        if Face_status:
            if X > old_X+10 or X < old_X-10:
                client.publish("backend/eyes/face/x", str(X))
                old_X = X
                print("x = ",X)
            if Y > old_Y+10 or Y < old_Y-10:
                client.publish("backend/eyes/face/y", str(Y))
                old_Y = Y
                print("Y = ",Y)
    else:
        client.publish("module/eyes/skin/see","0")



cap.release()
cv2.destroyAllWindows()
client.disconnect()
