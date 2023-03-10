from machine import Timer, PWM, Pin, ADC
from time import sleep
import machine
from machine import TouchPad, Pin
import esp32
import network
import ntptime
import neopixel
import socket

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
    
# Global variables
global temp  # measure temperature sensor data
global hall  # measure hall sensor data
global red_led_state # string, check state of red led, ON or OFF
global RLED
global x 
global y
global z

def web_page():
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    temp, hall, red_led_state
    """
    temp = esp32.raw_temperature()
    hall = esp32.hall_sensor()
    if RLED.value() == 1:
        red_led_state = "ON"
    else:
        red_led_state = "OFF"
    
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    
    <form action="/variables">
    <label for="var1">Variable 1:</label>
    <input type="text" id="var1" name="var1"><br><br>
    <label for="var2">Variable 2:</label>
    <input type="text" id="var2" name="var2"><br><br>
    <label for="var3">Variable 3:</label>
    <input type="text" id="var3" name="var3"><br><br>
    <input type="submit" value="Submit">
    </form>
    
    <h1>Variable 1: """ + x + """</h1>
    <h1>Variable 1: """ + y + """</h1>
    <h1>Variable 1: """ + z + """</h1>
    
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

#INITIALIZE RED LED
RLED = Pin(13, Pin.OUT)
RLED.value(0)
WIFI_connect("iPhone2", "password")


addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

x = "No Input Yet"
y = "No Input Yet"
z = "No Input Yet"

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
            if("GET /?red_led=on" in line):
                RLED.value(1)
                #print("toggle ON--------------------------------------------------------------------------------------")
            elif("GET /?red_led=off" in line):
                RLED.value(0)
                #print("toggle OFF--------------------------------------------------------------------------------------")
            #print(line)
            if("POST" in line):
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
                            #print(el
                        print(element)
                        
    #client.send(web_page())
    client.send("HTTP/1.1 200 OK\nDate: Mon, 27 Jul 2009 12:28:53 GMT\nServer: Apache/2.2.14 (Win32)\nLast-Modified: Wed, 22 Jul 2009 19:15:56 GMT\nContent-Length: 88\nContent-Type: text/html\nConnection: Closed\n\ntemp=55/humidity=14/speed=75")
    #print(web_page())
    client.close()
