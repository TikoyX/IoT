import machine
import time
from scd30 import SCD30
import socket
import ssl
from network import LoRa
import ubinascii
import json

# constants for sensor
i2c = machine.I2C(2, machine.I2C.MASTER, baudrate=100000)
scd30 = SCD30(i2c, 0x61)

# Initialise LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('0000000000000000')
app_key = ubinascii.unhexlify('f8dd03cd074babef77dd9fe58b158f84')

# join a network using OTAA (Over the Air Activation)
#uncomment below to use LoRaWAN application provided dev_eui
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print('Joined')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)


f = open('data.txt', 'r')
data = f.readline()
f.close()

if(len(data) == 0):
    f = open('data.txt', 'w')
    data = " ".join(["humidity", "1", "1", "30.0"])
    f.write(data)
    f.close()

elif(len(data) > 0):
    data_parts = data.strip().split()
    measurement_type = str(data_parts[0])
    measurement_interval = int(data_parts[1])
    measurement_seconds = int(data_parts[2])
    latest_measurement_value = float(data_parts[3])

    while True:
        s.setblocking(True)

        # Wait for sensor data to be ready to read (by default every 2 seconds)
        while scd30.get_status_ready() != 1:
            time.sleep_ms(500)

        measurements = scd30.read_measurement()

        measurement_value = None
        if(measurement_type == 'humidity'):
            measurement_value = measurements[2]
        elif(measurement_type == 'temperature'):   
            measurement_value = measurements[1]
        elif(measurement_type == 'co2'):
            measurement_value = measurements[0]

        print("Value: " + str(measurement_value))
        print("Latest value: " + str(latest_measurement_value))
        print("Type: " + measurement_type)
        print("Interval: " + str(measurement_interval))
        print("Seconds: " + str(measurement_seconds))

        min_measurement_value = latest_measurement_value-measurement_interval
        max_measurement_value = latest_measurement_value+measurement_interval

        print("Min value: " + str(min_measurement_value))
        print("Max value: " + str(max_measurement_value))

        if(not(min_measurement_value <= measurement_value <= max_measurement_value)):
            s.setblocking(True)
            print("Send: " + str(measurement_value))
            s.send(str.encode(str(measurement_value)))
            s.setblocking(False)

            received = s.recv(64)

            print('Received: ', received)
            if (len(received) > 0):
                received_parts = received.decode().strip().split()
                measurement_type =  str(received_parts[0])
                measurement_interval = int(received_parts[1])
                measurement_seconds = int(received_parts[2])

            latest_measurement_value = measurement_value

        else:
            print("Inside range, I will sleep!")
            f = open('data.txt', 'w')
            data = " ".join([measurement_type, str(measurement_interval), str(measurement_seconds), str(latest_measurement_value)])
            f.write(data)
            f.close()
            machine.deepsleep(measurement_seconds*1000)

            
