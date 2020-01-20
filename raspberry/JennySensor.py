
import select
import numpy as np
import RPi.GPIO as GPIO
import time
import socket
global trial 
trial = 0
global indicator
indicator = 0 

import requests
import cv2
# define time of rapsberry (unit:1s)

def driver():
        data = [0 for i in range(40)]
        j = 0
        GPIO.setmode(GPIO.BOARD)
        time.sleep(3)
        GPIO.setup(7, GPIO.OUT)
        GPIO.output(7, GPIO.LOW)
        time.sleep(0.02)
        GPIO.output(7, GPIO.HIGH)
        GPIO.setup(7, GPIO.IN)
        
        while GPIO.input(7) == GPIO.LOW:
                continue
        while GPIO.input(7) == GPIO.HIGH:
                continue
        while j < 40:
                k = 0
                while GPIO.input(7) == GPIO.LOW:
                        continue
                while GPIO.input(7) == GPIO.HIGH:
                        k += 1
                        if k > 100:
                                break
                if k < 8:
                        data[j] = 0
                else:
                        data[j] = 1
                j += 1
        return data
        
def compute(data):
        #trial=0
        global trial
        lights = light()
        humidity_bit = data[0:8]
        humidity_point_bit = data[8:16]
        temperature_bit = data[16:24]
        temperature_point_bit = data[24:32]
        check_bit = data[32:40]
        humidity=int(''.join([str(x) for x in humidity_bit]),2)
        humidity_point=int(''.join([str(x) for x in humidity_point_bit]),2)
        temperature=int(''.join([str(x) for x in temperature_bit]),2)
        temperature_point=int(''.join([str(x) for x in temperature_point_bit]),2)
        check_num=int(''.join([str(x) for x in check_bit]),2)
        sum = humidity + humidity_point + temperature + temperature_point
        GPIO.cleanup()
     
        while sum == check_num:
            x = temperature
            y = humidity
            z = lights
            awsurl = "http://104.196.199.145:5000/turtle/post/sensor"
            feature = '{"trial": '+ str(trial) +', "temperature": '+str(x)+', "humidity": '+str(y)+',"light": '+str(z)+'}'
            _, _, host_orig, path = awsurl.split('/', 3)
            host, port = host_orig.split(':',2)
            addr = socket.getaddrinfo(host, port)[0][-1]
            s_aws = socket.socket()
            s_aws.connect(addr)
            post='POST /%s HTTP/1.1\r\nContent-length: %d\r\nContent-Type: application/json\r\nHost: %s\r\n\r\n%s' % (path,len(feature),host,feature)
            print(path)
            print(feature)
            s_aws.send(post.encode())
            s_aws.close()
            time.sleep(1)
            trial += 1

            time.sleep(10)
            compute(driver())
            
        else:
            time.sleep(0.1)
            compute(driver())

def light():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(16, GPIO.IN)
    lights = GPIO.input(16)
    #GPIO.cleanup()
    return lights

        
if __name__=='__main__':

    while True:
        compute(driver())
        
                                
        
    
    
       

