import RPi.GPIO as GPIO
import time
import socket
global trial 
trial = 0

from picamera.array import PiRGBArray
from picamera import PiCamera
import requests
import cv2

def capture(start, camera , group):
    camera.start_preview()
    time.sleep(0.1)
    for i in range(10):
        if (i > 4):
            camera.capture('/home/pi/Desktop/%s/%s.jpg' % (group,(i-5+start)))
        else:
            camera.capture('/home/pi/Desktop/%s/%s.jpg' % (group,(i+start)))
        
    url = 'http://104.196.199.145:5000/turtle/post/img/%s' % group
    for i in range(5):
        img_dir = '/home/pi/Desktop/%s/%s.jpg' % (group,(i+start))
        img_name = '%s.jpg' % (i+start)
        files = {'file':(img_name, open(img_dir,'rb'), 'image/jpeg')}
        requests.post(url, files=files)
    start = start + 5
    camera.stop_preview()
    return start
        
if __name__=='__main__':
    start = 3000
    end_t = 3500
    group = 'over'
    camera = PiCamera()
    camera.resolution = (360,240)
    camera.framerate = 90
    rawCapture=PiRGBArray(camera,size=(360,240))
    
    while (start < end_t):
        print("start: %s" % (start))
        new_start = capture(start,camera, group)
        start = new_start
        print("end")
        time.sleep(5)
        

