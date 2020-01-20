
import select
import numpy as np

from datetime import datetime
from threading import Timer
import sched

from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import json
import requests
import cv2


def capture(camera):
    camera.start_preview()
    time.sleep(3)
    for i in range(10):
        if (i > 4):
            camera.capture('/home/pi/Desktop/test/1%s.jpg' % (i-5))
        else:
            camera.capture('/home/pi/Desktop/test/1%s.jpg' % (i))
        
    url = 'http://104.196.199.145:5000/turtle/post/img/test'
    files = {}
    for i in range(5):
        img_dir = '/home/pi/Desktop/test/1%s.jpg' % (i)
        img_name = '1%s.jpg' % (i)
        file = {'file%s' %(i): (img_name, open(img_dir,'rb'), 'image/jpeg')}
        files.update(file)
    requests.post(url, files=files)
        
    camera.stop_preview()
        
def snapshot():
    content_type = 'image/jpeg'
    camera.resolution = (1024, 768)
    rawCapture=PiRGBArray(camera,size=(1024, 768))
        
    camera.start_preview()

    for i in range(1):
        camera.capture('/home/pi/Desktop/snapshots/2%s.jpg' % i)
                
    url = 'http://104.196.199.145:5000/turtle/post/img/snapshots'
        
    for i in range(1):
        img_dir = '/home/pi/Desktop/snapshots/2%s.jpg' % i
        img_name = '2%s.jpg' % i
        files = {'file':(img_name, open(img_dir,'rb'), 'image/jpeg')}
        requests.post(url, files=files)    
        
        camera.stop_preview()

def monitor(camera):
    content_type = 'image/jpeg'
    camera.start_preview()

    for i in range(7):
        if (i > 1):
            camera.capture('/home/pi/Desktop/test/3%s.jpg' % (i-1))
        else:
            camera.capture('/home/pi/Desktop/test/3%s.jpg' % (i)) 
    
    for i in range(7):
        if (i > 1):
            camera.capture('/home/pi/Desktop/test/3%s.jpg' % (i-1))
        else:
            camera.capture('/home/pi/Desktop/test/3%s.jpg' % (i))
    
    url = 'http://104.196.199.145:5000/turtle/post/img/test'
    files = {}

    for i in range(5):
        img_dir = '/home/pi/Desktop/test/3%s.jpg' % (i)
        img_name = '3%s.jpg' % (i)
        file = {'file%s' %(i): (img_name, open(img_dir,'rb'), 'image/jpeg')}
        files.update(file)
    requests.post(url, files=files)
        
    camera.stop_preview()


        
if __name__=='__main__':
    
    camera = PiCamera()
    camera.resolution = (360,240)
    camera.framerate = 90
    rawCapture=PiRGBArray(camera,size=(360,240))
    
    #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #server.setblocking(False)

    #server_address = ('192.168.43.53', 8090)
    #print ('starting up on %s port %s' % server_address)
    #server.bind(server_address)
    #server.listen(5)
    #server.settimeout(0.5)
    acl_time = -1
    
    requests.adapters.DAFAULT_RETRIES = 50
    s = requests.session()
    s.keep_alive = False
    
    
    while True:
        mode = "capture"
                
        url = 'http://104.196.199.145:5000/turtle/run'
        
        resp = s.get(url)
        result = json.loads(resp.content.decode("utf-8"))
        mode = result['status']
        g_time = result['time']
        
        
        if (mode == "capture"):
            print("capture")
            capture(camera)
            #indicator = 0
                
        elif(mode == "snapshot"):
            print("snapshot")
            snapshot()
            indicator = 0
            camera.resolution = (360,240)
            rawCapture=PiRGBArray(camera,size=(360,240))
                
        #elif(mode ==3):
        elif(mode == "monitor"):
            print("monitor")
            if(acl_time == -1):
                t0 = time.time()
                monitor(camera)
                t1 = time.time()
                print(t1-t0)
                acl_time = time.time()
            elif(time.time()-acl_time >= 60):
                monitor(camera)
                acl_time = time.time()
            #if (g_time >= 60):
            #    monitor(camera)
        else:
            print("nothing")
        
            
        
                                