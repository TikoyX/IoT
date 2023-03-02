# main.py -- put your code here!
import time
from machine import I2C
from scd30 import SCD30

i2c = I2C(2, I2C.MASTER, baudrate=100000)
scd30 = SCD30(i2c, 0x61)


while True:
    # Wait for sensor data to be ready to read (by default every 2 seconds)
    while scd30.get_status_ready() != 1:
        time.sleep_ms(200)
    ans = scd30.read_measurement()

    print("CO2: %d ppm, Temperature: %0.2f C, Humidity: %0.2f %%" % (ans[0], ans[1], ans[2]))


# Is the SCD30 an analog or digital sensor?
# Digital

# How do we translate from an analog signal to a digital one? Is there any loss of information?
# We use an ADC to convert the analog signal to a digital one. There is some loss of information.

# Are the measurements it gives correct? What might influence them?
# There might be some influence currently from me since i am sitting so close to the sensor.
# The CO2 is about 600-700 when i am nore in front of the sensor and then increases to about 2800 when i am.
# There can also be heating effects from the pcb that can be offset.

# How do we even know if they're correct? Can we take steps to ensure or check for correctness?
# We can check the data against other sensors and compare the results. We should 