# mac: fc:f5:c4:0e:14:84

from network import LoRa
import machine
import time
from scd30 import SCD30
import socket
import binascii
import struct

# constants
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
i2c = machine.I2C(2, machine.I2C.MASTER, baudrate=100000)
scd30 = SCD30(i2c, 0x61)

# create an OTAA authentication parameters, change them to the provided credentials
app_eui = ubinascii.unhexlify('0000000000000000')
app_key = ubinascii.unhexlify('f8dd03cd074babef77dd9fe58b158f84')
#uncomment to use LoRaWAN application provided dev_eui
#dev_eui = ubinascii.unhexlify('70B3D549938EA1EE')


# join a network using OTAA (Over the Air Activation)
#uncomment below to use LoRaWAN application provided dev_eui
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
#lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not joined yet...')

print('Joined')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

while True:
    s.setblocking(True)
    s.send(str.encode(str("hej")))
    s.setblocking(False)

    received = s.recv(64)
    #received = s.recv(10000)
    print('received: ', received)

    if (len(received) > 0):
        
        # Wait for sensor data to be ready to read (by default every 2 seconds)

        s.setblocking(True)

        while scd30.get_status_ready() != 1:
            time.sleep_ms(500)
        ans = scd30.read_measurement()
        
        # convert the answers to byte
        answer = None
        if(received == b'humidity'):
            answer = ans[2]
        elif(received == b'temperature'):   
            answer = ans[1]
        elif(received == b'co2'):
            answer = ans[0]

        s.send(str.encode(str(answer)))

        s.setblocking(False)