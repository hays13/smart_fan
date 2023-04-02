import dht, time
from time import sleep
from machine import Pin

DHT_PIN = 14

# Create a DHT object with the DHT22 sensor type
sensor = dht.DHT22(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))

while True:
    try:
        # Read the temperature and humidity values from the sensor
        sleep(2) #reads in every x seconds
        sensor.measure()
        temperature = sensor.temperature()
        temperature = temperature * 1.8 + 32 #converts from C to F
        humidity = sensor.humidity()

        # Print the values to the serial console
        print("Temperature: {:.1f}°F, Humidity: {:.1f}%".format(temperature, humidity))

    except OSError as e:
        print("Failed to read sensor:", e)
