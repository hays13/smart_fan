import requests, datetime, kivy
from machine import Timer
from kivy.network.urlrequest import UrlRequest

def set_fan_speed(fan_speed):
    # send corresponding fan speed to power relay
    # push current fan_speed value to server
    url = 'http://172.20.10.8/fan_speed={}/'.format(fan_speed)
    try:
        UrlRequest.post(url)
    except:
        print("cannot connect to server")

def get_time():
    t = datetime.datetime.now()
    hour = t.hour
    minute = t.minute
    return hour, minute

def read_sensor(timer):
    #################################################
    # turning on fan equals setting fan speed to 50 #
    # turning off fan equals setting fan speed to 0 #
    #################################################
    
    # requesting current inputs from HTMLserver
    SERVER = 'http://172.20.10.8'
    result = requests.get(SERVER)
    resultList = result.split("/")

    # load currTemp from sensor
    # currTemp = load_from_sensor()
    # load maxTemp from server
    maxTemp = [s.split('=')[1] for s in resultList if "max_temp=" in s]
    # load minTemp from server
    minTemp = [s.split('=')[1] for s in resultList if "min_temp=" in s]
    
    # load currHumd from sensor
    # currHumd = load_from_sensor()
    # load maxHumd from server
    maxHumd = [s.split('=')[1] for s in resultList if "max_humidity=" in s]
    # load minHumd from server
    minHumd = [s.split('=')[1] for s in resultList if "min_humidity=" in s]
    
    # load list of schedules
    schedule = [s.split('=')[1] for s in resultList if "schedule=" in s]
    # load current time
    curr_hour, curr_min = get_time()
    curr_time = curr_hour * 60 + curr_min
    
    on_counter = 0
    
    # if statements to determine what values to change
    if currTemp > maxTemp:
        # turn on fan
        on_counter += 1
        # send fan speed to server
    elif currTemp < minTemp:
        # turn off fan
        pass
        # send fan speed to server
    if currHumd > maxHumd:
        # turn on fan
        on_counter += 1
        # send fan speed to server
    elif currHumd < minHumd:
        # turn off fan
        pass
        # send fan speed to server
    # unsure of format of schedules: assuming an input of a 2D array schedule = [[start, end], ...]  [11:15, 13:30]
    if len(schedule) > 0: # if there is a schedule set
        fan_counter = 0
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
            on_counter += 1
            # send fan speed to server
        else:
            # turn off fan
            pass
            # send fan speed to server
            
    if on_counter > 0:
        set_fan_speed(50)
        return
    else:
        set_fan_speed(0)
        return

def read_fundamentals(timer):
    # requesting status fan speed
    # read fan_speed from server, then send the corresponding speed to the relay (calling the corresponding mode)
    SERVER = 'http://172.20.10.8'
    result = UrlRequest.get(SERVER)
    resultList = result.split("/")
    
    fan_speed = [s.split('=')[1] for s in resultList if "speed=" in s]
    set_fan_speed(fan_speed)

if __name__ == "__main__":
    T0 = Timer(0)
    T1 = Timer(1)
    T0.init(period=15000, mode=Timer.PERIODIC, callback=read_sensor) #runs every 15 seconds
    T1.init(period=1000, mode=Timer.PERIODIC, callback=read_fundamentals) #runs every 1 second
