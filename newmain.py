from machine import Timer, PWM, Pin
from time import sleep
import network
import ntptime
import socket

class DCMotor:      
    def __init__(self, pin1, pin2, enable_pin, min_duty=750, max_duty=1023):
        self.pin1=pin1
        self.pin2=pin2
        self.enable_pin=enable_pin
        self.min_duty = min_duty
        self.max_duty = max_duty

    def forward(self,speed):
        self.speed = speed
        self.enable_pin.duty(self.duty_cycle(self.speed))
        self.pin1.value(0)
        self.pin2.value(1)
    
    def backwards(self, speed):
        self.speed = speed
        self.enable_pin.duty(self.duty_cycle(self.speed))
        self.pin1.value(1)
        self.pin2.value(0)

    def stop(self):
        self.enable_pin.duty(0)
        self.pin1.value(0)
        self.pin2.value(0)
    
    def duty_cycle(self, speed):
        if self.speed <= 0 or self.speed > 100:
            duty_cycle = 0
        else:
            duty_cycle = int(self.min_duty + (self.max_duty - self.min_duty)*((self.speed-1)/(100-1)))
        return duty_cycle

def WIFI_connect(ssid, password):
    
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected() == False:
        print("connecting to network...")
        sta_if.active(True)
        #print(sta_if.scan())
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass
    iplist = sta_if.ifconfig()
    print("Connected to " + ssid)
    print("IP ADDRESS: " + iplist[0])

def parseData(result):
    global current_temp, current_hum, fan_speed, schedule, maxHumd, minHumd, maxTemp, minTemp
    resultList = result.split("/")
    current_temp = [s.split('=')[1] for s in resultList if "temp=" in s][0]
    current_hum = [s.split('=')[1] for s in resultList if "humidity=" in s][0]
    fan_speed = [s.split('=')[1] for s in resultList if "speed=" in s][0]
    schedule = [s.split('=')[1] for s in resultList if "schedule=" in s]
    maxHumd = [s.split('=')[1] for s in resultList if "maxHumd=" in s][0]
    minHumd = [s.split('=')[1] for s in resultList if "minHumd=" in s][0]
    maxTemp = [s.split('=')[1] for s in resultList if "MaxTemp=" in s][0]
    minTemp = [s.split('=')[1] for s in resultList if "minTemp=" in s][0]

# Global variables
'''global current_temp
global current_hum
global fan_speed
global schedule # list of tuples [[start, end], ...]
global maxHumd
global minHumd
global maxTemp
global minTemp'''

WIFI_connect("iPhone2", "password")


addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

frequency = 15000       
pin1 = Pin(12, Pin.OUT)    
pin2 = Pin(13, Pin.OUT)     
enable = PWM(Pin(15), frequency)  
dc_motor = DCMotor(pin1, pin2, enable)    

while(True):
    #print("WHILE----------------------------------")
    client, addr = s.accept()
    text = client.makefile('rwb', 0)
    while(True):
        line = text.readline()
        #print(line)
        if(not line or line == b'\r\n'):
            #print("BREAK\n\n")
            break
        else:
            if("POST" in line):
                parseData(line)
                if(fan_speed > 0):
                    dc_motor.forward(fan_speed)
                elif(fan_speed <= 0):
                    dc_motor.stop()
                
                #print("LINE1: \n")
                #print(line)
                #print("LINE2: \n")
                #print(line.decode())
                #print("LINE3: \n")
                #print(line.decode().split("/"))
                line_list = line.decode().split("/")
                for element in line_list:
                    if '=' in element:
                        #if ' ' in element:
                            #element2 = element.split(" ")
                            #print(element)
                        print(element)
                        
    #client.send(web_page())
    ### temp={}/humidity={}/speed={}/schedule={}/maxHumd={}/minHumd{}/maxTemp={}/minTemp={}, (temp, humd, speed, schedule, maxHumd, minHumd, maxTemp, minTemp)
    client.send("HTTP/1.1 200 OK\nDate: Mon, 27 Jul 2009 12:28:53 GMT\nServer: Apache/2.2.14 (Win32)\nLast-Modified: Wed, 22 Jul 2009 19:15:56 GMT\nContent-Length: 88\nContent-Type: text/html\nConnection: Closed\n\ntemp={}/humidity={}/speed={}/schedule={}/maxHumd={}/minHumd{}/maxTemp={}/minTemp={}".format(temp, humd, speed, schedule, maxHumd, minHumd, maxTemp, minTemp))
    #print(web_page())
    client.close()

'''
#Example code
from dcmotor import DCMotor       
from machine import Pin, PWM   
from time import sleep     
frequency = 15000       
pin1 = Pin(12, Pin.OUT)    
pin2 = Pin(13, Pin.OUT)     
enable = PWM(Pin(15), frequency)  
dc_motor = DCMotor(pin1, pin2, enable)      
dc_motor.forward(20)    
sleep(5)        
dc_motor.stop()  
sleep(2)
dc_motor.forward(5)
sleep(5)
dc_motor.stop()'''
