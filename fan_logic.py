import esp32, requests, network
from machine import Timer


def set_fan_speed(fan_speed):
    # send corresponding fan speed to power relay
    return
    

def read_sensor(timer):
    #################################################
    # turning on fan equals setting fan speed to 50 #
    # turning off fan equals setting fan speed to 0 #
    #################################################
    SERVER = 'http://172.20.10.8'
    # requesting current inputs from HTMLserver
    result = requests.get(SERVER)
    resultList = result.split("/")

    # load currTemp from sensor
    # currTemp = 
    # load maxTemp from server
    maxTemp = [s.split('=')[1] for s in resultList if "max_temp=" in s]
    # load minTemp from server
    minTemp = [s.split('=')[1] for s in resultList if "min_temp=" in s]
    
    # load currHumd from sensor
    # currHumd = 
    # load maxHumd from server
    maxHumd = [s.split('=')[1] for s in resultList if "max_humidity=" in s]
    # load minHumd from server
    minHumd = [s.split('=')[1] for s in resultList if "min_humidity=" in s]
    
    # load list of schedules
    schedule = [s.split('=')[1] for s in resultList if "schedule=" in s]
    # load current time
    # time = 
    
    # if statements to determine what values to change
    if currTemp > maxTemp:
        # turn on fan
        set_fan_speed(50)
        # send fan speed to server
    elif currTemp < minTemp:
        # turn off fan
        set_fan_speed(0)
        # send fan speed to server
    if currHumd > maxHumd:
        # turn on fan
        set_fan_speed(50)
        # send fan speed to server
    elif currHumd < minHumd:
        # turn off fan
        set_fan_speed(0)
        # send fan speed to server
    # unsure of format of schedules: assuming an input of a 2D array schedule = [[start, end], ...]
    if len(schedule) > 0: # if there is a schedule set
        fan_counter = 0
        for s in range(len(schedule)):
            start = schedule[s][0]
            end = schedule[s][1]
            if time >= start and time < end:
                fan_counter += 1
        if fan_counter > 0:
            # turn on fan
            set_fan_speed(50)
            # send fan speed to server
        else:
            # turn off fan
            set_fan_speed(0)
            # send fan speed to server

def read_fundamentals(timer):
    # requesting status of manual on/off and fan speed
    # if fan_speed > 0, turn fan on to that speed
    # read fan_speed from server, then send the corresponding speed to the relay (calling the corresponding mode)
    SERVER = 'http://172.20.10.8'
    result = requests.get(SERVER)
    resultList = result.split("/")
    
    fan_speed = [s.split('=')[1] for s in resultList if "speed=" in s]
    set_fan_speed(fan_speed)
    

if __name__ == "__main__":
    #connect2wifi()
    T0 = Timer(0)
    T1 = Timer(1)
    T0.init(period=15000, mode=Timer.PERIODIC, callback=read_sensor) #runs every 15 seconds
    T1.init(period=1000, mode=Timer.PERIODIC, callback=read_fundamentals) #runs every 1 second
