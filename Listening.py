import pyaudio
import wave
import os
import math, numpy as np
import threading
import speech_recognition as sr
import threading
import time
import re

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE =48000

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


def _listening():
    STATE ="start"
    frames = []
    t = float(0)
    t1 = float(0)

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data_conv  = np.fromstring(data, dtype=np.int16)
        max = np.max(data_conv)
        
        frames.append(data)

        print(max)
        if STATE == "start":
            t = time.time()
            STATE = "rec"
            
        elif time.time()-t > float(3)  and STATE == "rec" and max < 7000:
            frames = []
            STATE = "start"   

        elif max > 7000 :
            STATE = "wait"

        elif STATE =="wait" and max<7000:
            t1 = time.time() 
            STATE = "save"

        elif max < 7000 and STATE =="save" and time.time()-t1 > float(1) :
            STATUS = "mosquitto_pub -u username -P hcilab -t module/status/led -m {}".format("1,2")
            os.system(STATUS)
            STATE = "start"
            wf = wave.open('t.wav', 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            frames = []
            r = sr.Recognizer()
            print("LOL")
            with sr.AudioFile("t.wav") as source:   
                audio = r.record(source)
            try:    
                text = r.recognize_google(audio)
                print(text)
                cmd = "mosquitto_pub -u username -P hcilab -t backend/listening/text -m {}".format(text)
                os.system(cmd)

            except Exception as e:
                print("bb")
      
    stream.stop_stream()
    stream.close()
    p.terminate()

_listening()
        
    
