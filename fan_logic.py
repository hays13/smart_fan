import requests, datetime, dht
from machine import Timer, Pin
from kivy.network.urlrequest import UrlRequest

def set_fan_speed(fan_speed):
    # send corresponding fan speed to power relay
    # push current fan_speed value to server
    SERVER = 'http://172.20.10.8'
    result = UrlRequest.get(SERVER)
    resultList = result.split("/")
    
    fan_speed_server = [s.split('=')[1] for s in resultList if "speed=" in s][0]
    if fan_speed == 50: #turns on fan
        url = '{}/speed={}/'.format(SERVER, fan_speed)
    elif fan_speed == 1: #retains current speed
        url = '{}/speed={}/'.format(SERVER, fan_speed_server)
    elif fan_speed == 0: #turns off fan
        url = '{}/speed={}/'.format(SERVER, fan_speed)
    else:
        print("Problem updating fan_speed")
    # posts to server
    try:
        UrlRequest.post(url)
    except:
        print("Cannot connect to server")

def get_time():
    t = datetime.datetime.now()
    hour = t.hour
    minute = t.minute
    return hour, minute

def read_sensor(sensor):
    sensor.measure()
    temperature = sensor.temperature()
    temperature = temperature * 1.8 + 32 #converts from C to F
    humidity = sensor.humidity()
    
    return temperature, humidity

def schedule_control(schedule, curr_time):
    fan_counter = 0
    if len(schedule) > 0: # if there is a schedule set
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

def read_server(timer):
    #################################################
    # turning on fan equals setting fan speed to 50 #
    # turning off fan equals setting fan speed to 0 #
    #################################################
    
    # requesting current inputs from HTMLserver
    SERVER = 'http://172.20.10.8'
    result = requests.get(SERVER)
    resultList = result.split("/")
    sensor = dht.DHT22(Pin(14, Pin.IN, Pin.PULL_UP))

    # load currTemp and currHumd from sensor
    currTemp, currHumd = read_sensor(sensor)
    # load maxTemp from server
    maxTemp = [s.split('=')[1] for s in resultList if "max_temp=" in s][0]
    # load minTemp from server
    minTemp = [s.split('=')[1] for s in resultList if "min_temp=" in s][0]
    
    # load maxHumd from server
    maxHumd = [s.split('=')[1] for s in resultList if "max_humidity=" in s][0]
    # load minHumd from server
    minHumd = [s.split('=')[1] for s in resultList if "min_humidity=" in s][0]
    
    # load list of schedules
    schedule = [s.split('=')[1] for s in resultList if "schedule=" in s] # [[start_time, end_time], ...]
    # load current time
    curr_hour, curr_min = get_time()
    curr_time = curr_hour * 60 + curr_min
    
    on_counter = 0
    off_counter = 0
    
    # if statements to determine what values to change
    if ~(maxTemp == None) and ~(minTemp == None):
        if currTemp > maxTemp:
            # turn on fan
            on_counter += 1
        
        elif currTemp < minTemp:
            # turn off fan
            off_counter += 1
    
    if ~(maxHumd == None) and ~(minHumd == None):
        if currHumd > maxHumd:
            # turn on fan
            on_counter += 1
            
        elif currHumd < minHumd:
            # turn off fan
            off_counter += 1
        
    # assuming an input of a 2D array schedule = [[start, end], ...] (ie. [11:15, 13:30])
    fan_counter = schedule_control(schedule, curr_time)
    if fan_counter == 1:
        on_counter += 1
    elif fan_counter == -1:
        off_counter += 1
    else:
        print("Error controlling fan")
            
    if on_counter > 0:
        # turns on fan
        set_fan_speed(50)
    elif off_counter > 0:
        # turns of fan
        set_fan_speed(0)
    else:
        set_fan_speed(1)

if __name__ == "__main__":
    T0 = Timer(0)
    T0.init(period=15000, mode=Timer.PERIODIC, callback=read_sensor) #runs every 15 seconds
