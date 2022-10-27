import uasyncio
import random
import WIFI_CONFIG
import time
import sys
import sdcard
import uos
import jpegdec
from machine import Pin, SPI
from network_manager import NetworkManager
from urllib import urequest
from pcf85063a import PCF85063A
from pimoroni_i2c import PimoroniI2C

import gc

from picographics import PicoGraphics, DISPLAY_INKY_FRAME

"""
You *must* insert an SD card into Inky Frame!
We need somewhere to save the png for display.
"""

#################################
# ----- INITIALIZE SYSTEM ----- #
#################################

gc.collect()

I2C_SDA_PIN = 4
I2C_SCL_PIN = 5
HOLD_VSYS_EN_PIN = 2

# Enable vsys to stay awake
hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
hold_vsys_en_pin.value(True)

# Intialize the PCF85063A real time clock chip
i2c = PimoroniI2C(I2C_SDA_PIN, I2C_SCL_PIN, 100000)
rtc = PCF85063A(i2c)

UPDATE_INTERVAL = 30

activity_led = Pin(6, Pin.OUT)
wireless_led = Pin(7, Pin.OUT)

gc.collect()

##############################
# ----- DOWNLOAD TASKS ----- #
##############################
rtc.enable_timer_interrupt(True)

activity_led.on()

# Mount SD Card
sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
sd = sdcard.SDCard(sd_spi, Pin(22))
uos.mount(sd, "/sd")

wireless_led.on()

# Connect to network
def status_handler(mode, status, ip):
    print(mode, status, ip)

network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

gc.collect()

display = PicoGraphics(DISPLAY_INKY_FRAME)
WIDTH, HEIGHT = display.get_bounds()
FILENAME = "/sd/current-tasks.jpg"

##########################################################
#--------------------------------------------------------#
ENDPOINT = "https://YOURHOSTNAME/static/current_tasks.jpg"
#--------------------------------------------------------#
##########################################################

# ENDPOINT must be public resource because
# urllib.urequest does not support auth and
# urequests is too memory intensive

gc.collect()
# Get and assign data
url_endpoint = ENDPOINT.format(WIDTH, HEIGHT + random.randint(0, 10))
gc.collect()

socket = urequest.urlopen(url_endpoint)
data = bytearray(1024)
with open(FILENAME, "wb") as f:
    while True:
        if socket.readinto(data) == 0:
            break
        f.write(data)
socket.close()
print("Tasks downloaded")
gc.collect()

# Disconnect from wifi
def disconnect():
    network_manager.disconnect()
    if not network_manager.isconnected():
        wireless_led.init(Pin.IN)
        print("Disconnected from wireless")
    else:
        print("Disconnecting...")
        disconnect()

disconnect()

jpeg = jpegdec.JPEG(display)
gc.collect()

display.set_pen(1)
display.clear()

jpeg.open_file(FILENAME)
jpeg.decode()

display.update()

gc.collect()

activity_led.init(Pin.IN)

# Sleep until next update
rtc.set_timer(UPDATE_INTERVAL, ttp=PCF85063A.TIMER_TICK_1_OVER_60HZ)
hold_vsys_en_pin.init(Pin.IN)
time.sleep(UPDATE_INTERVAL * 60)

sys.exit()
