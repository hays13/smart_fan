from machine import Timer, PWM, Pin
from time import sleep
import time
import network
import ntptime
import socket
import dht
import machine     

rtc = machine.RTC()
ntptime.host = "pool.ntp.org"

def update_time(rtc):
    count = 0
    while(True):
        try:
            ntptime.settime()
        except:
            #print("FAIL")
            sleep(1)
            continue
        else:
            break
    #print(rtc.datetime())
    year, month, day, weekday, hours, minutes, seconds, subseconds = rtc.datetime()
    rtc.datetime((year, month, day, weekday, (hours-4), minutes, seconds, subseconds))

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

def schedule_control(schedule, curr_time):
    fan_counter = 0
     # if there is a schedule set
    for s in range(len(schedule)):
            start = int(schedule[s][0])
            end = int(schedule[s][1])
            # converts start time to minutes
            start = start.split(':')
            start_hour = int(start[0])
            start_min = int(start[1])
            start_val = start_hour * 60 + start_min
            # converts end time to minutes
            end = end.split(':')
            end_hour = int(end[0])
            end_min = int(end[1])
            end_val = end_hour * 60 + end_min
            
            if  curr_time > start_val and curr_time < end_val:
                fan_counter += 1
    if fan_counter > 0:
        # turn on fan
        return 1
    else:
        # turn fan off
        return -1

def read_sensor(sensor):
    sensor.measure()
    temperature = sensor.temperature()
    temperature = temperature * 1.8 + 32 #converts from C to F
    humidity = sensor.humidity()
    
    return temperature, humidity

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
    print(result.decode())
    resultList = result.decode().split("/")
    print(resultList)
    for s in resultList:
        if "speed=" in s:
            fan_speed = int(s.split('=')[1])
            print("fan_speed = " + str(fan_speed))
        if "schedule=" in s:
            schedule = s.split('=')[1]
            print("schedule = " + str(schedule))
        if "max_humid=" in s:
            maxHumd = int(s.split('=')[1])
            print("maxHumd = " + str(maxHumd))
        if "min_humid=" in s:
            minHumd = int(s.split('=')[1])
            print("minHumd = " + str(minHumd))
        if "max_temp=" in s:
            maxTemp = int(s.split('=')[1])
            print("maxTemp = " + str(maxTemp))
        if "min_temp=" in s:
            minTemp = int(s.split('=')[1])
            print("minTemp = " + str(minTemp))
    '''fan_speed = [s.split('=')[1] for s in resultList if "speed=" in s]
    schedule = [s.split('=')[1] for s in resultList if "schedule=" in s]
    maxHumd = [s.split('=')[1] for s in resultList if "max_humid=" in s]
    minHumd = [s.split('=')[1] for s in resultList if "min_humid=" in s]
    maxTemp = [s.split('=')[1] for s in resultList if "max_temp=" in s]
    minTemp = [s.split('=')[1] for s in resultList if "min_temp=" in s]'''   
    

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
fan_speed = 0
pin1 = Pin(12, Pin.OUT)    
pin2 = Pin(13, Pin.OUT)     
enable = PWM(Pin(15), frequency)  
dc_motor = DCMotor(pin1, pin2, enable)
scedule_toggle = 0
fan_counter = 0
sensor = dht.DHT22(Pin(14, Pin.IN, Pin.PULL_UP))
schedule_count = 0
schedule = []
minHumd = 0
maxHumd = 100000
minTemp = 0
maxTemp = 100000
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
                current_temp, current_hum = read_sensor(sensor)
                client.send("HTTP/1.1 200 OK\nDate: Mon, 27 Jul 2009 12:28:53 GMT\nServer: Apache/2.2.14 (Win32)\nLast-Modified: Wed, 22 Jul 2009 19:15:56 GMT\nContent-Length: 88\nContent-Type: text/html\nConnection: Closed\n\ntemp={}/humidity={}/speed={}/schedule={}/maxHumd={}/minHumd{}/maxTemp={}/minTemp={}".format(current_temp, current_hum, fan_speed, schedule, maxHumd, minHumd, maxTemp, minTemp))
                ### temp={}/humidity={}/speed={}/schedule={}/maxHumd={}/minHumd{}/maxTemp={}/minTemp={}, (temp, humd, speed, schedule, maxHumd, minHumd, maxTemp, minTemp)
    client.close()
        
        
        
    
    update_time(rtc)
    year, month, day, weekday, hours, minutes, seconds, subseconds = rtc.datetime()
    
    schedule_toggle = fan_counter
    if len(schedule) > 0 and schedule != []:
        fan_counter = schedule_control(schedule, hours*60+minutes)
    if schedule != []:
        print("schedule_control({},{}) = {}".format(schedule,hours*60+minutes,fan_counter))
    if fan_counter != schedule_toggle:
        if fan_counter == 1:
            if fan_speed == 0:
                fan_speed = 20
        else:
            fan_speed = 0
    
    current_temp, current_hum = read_sensor(sensor)
    if current_temp > maxTemp:
        # turn on fan
        if fan_speed == 0:
            fan_speed = 20
    elif current_temp < minTemp:
        # turn off fan
        fan_speed = 0
    elif current_hum > maxHumd:
        # turn on fan
        if fan_speed == 0:
            fan_speed = 20
    elif current_hum < minHumd:
        # turn off fan
        fan_speed = 0   
    
    print("FANNNNNNN : " + str(fan_speed))    
    if(fan_speed > 0):
        dc_motor.forward(fan_speed)
        print("ON")
    elif(fan_speed <= 0):
        dc_motor.stop()
        print("OFF")
            

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
