import uasyncio
import _thread
import WIFI_CONFIG
import urequests
import time
import sys
from machine import Pin, PWM
from network_manager import NetworkManager
from secrets import api_key, url
from pcf85063a import PCF85063A
from pimoroni_i2c import PimoroniI2C

import gc

from picographics import PicoGraphics, DISPLAY_INKY_FRAME, PEN_RGB332

#################################
# ----- INITIALIZE SYSTEM ----- #
#################################

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
activity_PWM = PWM(Pin(6))
activity_PWM.freq(1000)

wireless_led = Pin(7, Pin.OUT)
wireless_PWM = PWM(Pin(7))
wireless_PWM.freq(1000)

display = PicoGraphics(DISPLAY_INKY_FRAME)
WIDTH, HEIGHT = display.get_bounds()

##############################
# ----- DEFINE METHODS ----- #
##############################

def status_handler(mode, status, ip):
    print(mode, status, ip)
    
network_manager = NetworkManager(WIFI_CONFIG.COUNTRY, status_handler=status_handler)

def pulse_wifi_led():
    while transmitting:
        for duty in range(0, 65025, 5):
            wireless_PWM.duty_u16(duty)
            time.sleep(0.0001)
        for duty in range(65025, 0, -5):
            wireless_PWM.duty_u16(duty)
            time.sleep(0.0001)

def drawBox(x: int, y: int, status: str):
    if status == "open":
        display.set_pen(0)
        display.line(x + 3, y + 1, x + 13, y + 1) # top
        display.line(x + 13, y + 1, x + 15, y + 3) # UR corner
        display.line(x + 15, y + 3, x + 15, y + 13) # right
        display.line(x + 15, y + 13, x + 13, y + 15) # LR corner
        display.line(x + 14, y + 15, x + 3, y + 15) # bottom
        display.line(x + 3, y + 15, x + 1, y + 12) # LL corner
        display.line(x + 1, y + 13, x + 1, y + 3) # left
        display.line(x + 1, y + 3, x + 3, y + 1) # UL corner
    elif status == "completed":
        display.set_pen(3)
        display.polygon([
            (x + 4, y),
            (x + 13, y),
            (x + 15, y + 3),
            (x + 15, y + 13),
            (x + 13, y + 15),
            (x + 3, y + 15),
            (x + 1, y + 13),
            (x + 1, y + 4),
        ])
        display.set_pen(1)
        display.line(x + 5, y + 8, x + 7, y + 10)
        display.line(x + 7, y + 10, x + 13, y + 4)

def cleanText(task: str) -> str:
    BADCHARS = {
        "’": "'",
        "—": "",
        "…": "..."
    }
    
    j = 0
    text = ""
    
    while j < len(task):
        char = task[j]
    
        if char in BADCHARS:
            text += BADCHARS[char]
        else:
            text += char
        
        j += 1
    
    return text

#####################################
# ----- LOOP EVERY 30 MINUTES ----- #
#####################################
rtc.enable_timer_interrupt(True)

for duty in range(0, 65025, 5):
    activity_PWM.duty_u16(duty)
    time.sleep(0.0001)

for duty in range(0, 65025, 5):
    wireless_PWM.duty_u16(duty)
    time.sleep(0.0001)
    
# Pulse network led
print("Connecting...")
transmitting = True
# ----- Line 128 was previously working but now causes error:
# ----- SError: (-17040, 'MBEDTLS_ERR_RSA_PUBLIC_FAILED+MBEDTLS_ERR_MPI_ALLOC_FAILED')
#
# _thread.start_new_thread(pulse_wifi_led, ())

# Connect to network and most recent version of tasks
uasyncio.get_event_loop().run_until_complete(network_manager.client(WIFI_CONFIG.SSID, WIFI_CONFIG.PSK))

gc.collect()

# Get and assign data
data = urequests.get(url(), headers={"Authorization":"Bearer","access_token":api_key()}).json()
print("Tasks downloaded")

# Disconnect from wifi
while network_manager.isconnected():
    network_manager.disconnect()
if not network_manager.isconnected():
    print("Disconnected")
    transmitting = False
    for duty in range(65025, 0, -5):
        wireless_PWM.duty_u16(duty)
        time.sleep(0.0001)
    wireless_led.init(Pin.IN)

gc.collect()

# Initialize graphics and draw title
display.set_pen(1)
display.clear()

display.set_pen(3)
display.set_font("bitmap6")
display.text("Today's Tasks", 15, 15, scale = 5)

x = 45
y = 60
i = 0

display.set_font("sans")

gc.collect()

# Draw all tasks until display is full
while y < HEIGHT - 30 and i < len(data["tasks"]):
    item = data["tasks"][i]
    drawBox(15, y + 3, item["status"])
    display.set_pen(0)
    display.text(cleanText(item["name"]), x, y + 12, scale = 1)
    y += 33
    i += 1

print("Updating display")
display.update()

gc.collect()

# Turn off activity led
print("Going to sleep...")
for duty in range(65025, 0, -5):
    activity_PWM.duty_u16(duty)
    time.sleep(0.0001)
activity_led.init(Pin.IN)

# Sleep until next update
rtc.set_timer(UPDATE_INTERVAL, ttp=PCF85063A.TIMER_TICK_1_OVER_60HZ)
hold_vsys_en_pin.init(Pin.IN)
time.sleep(UPDATE_INTERVAL * 60)

sys.exit()
