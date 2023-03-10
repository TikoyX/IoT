from network import WLAN
import machine
import time
from scd30 import SCD30
import socket

# constants for the wifi connection and sensor
i2c = machine.I2C(2, machine.I2C.MASTER, baudrate=100000)
scd30 = SCD30(i2c, 0x61)
wlan = WLAN(mode=WLAN.STA)

# Setup for WiFi connection
wlan.connect(ssid='earl grey', auth=(WLAN.WPA2, 'tebrevet'))
while not wlan.isconnected():
    machine.idle()
    time.sleep_ms(1000)
    print("Connecting to WiFi...")
print("WiFi connected succesfully")
print(wlan.ifconfig())

time.sleep(1)

# setup socket for connection
s = socket.socket()
host = '192.168.4.1'
addr = socket.getaddrinfo(host,1234)[0][-1]
s.connect(addr)
print('socket connected')

while True:
    received = s.recv(10000)
    print('received: ', received)

    if (len(received) > 0):
        
        # Wait for sensor data to be ready to read (by default every 2 seconds)
        while scd30.get_status_ready() != 1:
            time.sleep_ms(500)
        ans = scd30.read_measurement()
        
        # convert the answers to byte
        if(received == b'humidity'):
            s.send(str.encode(str(ans[2])))
        elif(received == b'temperature'):   
            s.send(str.encode(str(ans[1])))
        elif(received == b'co2'):
            s.send(str.encode(str(ans[0])))
