
import BlynkLib
from BlynkTimer import BlynkTimer
import network
import machine
from machine import Pin
import time
import gc


WIFI_SSID = 'elMeuWifi'
WIFI_PASS = 'elMeuPass'

BLYNK_AUTH = 'elMeuTokenDeBlynk'
led16 = Pin(16, Pin.OUT)
timer = BlynkTimer()

try:
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.active(False)
        time.sleep(1)
        wifi.active(True)
        wifi.connect(WIFI_SSID, WIFI_PASS)
        timeout = 0
        while (not wifi.isconnected() and timeout < 20):
            print(20 - timeout)
            timeout = timeout + 1
            time.sleep(2)
        if(wifi.isconnected()):
            print('connected')
            # wifi_OK = 1
        else:
            print('not connected, reset')
            machine.reset()
            # wifi_OK = 0
except:
    print('error, reset')
    machine.reset()
        

print('IP:', wifi.ifconfig()[0])

try:
    blynk = BlynkLib.Blynk(BLYNK_AUTH,
                       insecure=True,          # disable SSL/TLS
                       server='blynk.cloud',   # set server address
                       port=80,                # set server port
                       heartbeat=30           # set heartbeat to 30 secs
                       )

    #blynk = BlynkLib.Blynk(BLYNK_AUTH, insecure = True, port = 80, heartbeat = 30)
except:
    print('error, reset')
    machine.reset()

@blynk.on("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')

@blynk.on("disconnected")
def blynk_disconnected():
    print('Blynk disconnected')
    print('error, reset')
    machine.reset()
    
@blynk.on("V1")
def v1_write_handler(value):
    print('Current slider value: {}'.format(value[0]))


@blynk.on("V*")
def blynk_handle_vpins(pin, value):
    print("V{} value: {}".format(pin, value))

def blink_led():
    led16.value (not led16.value())
def print_uptime():
    uT = time.ticks_ms()/1000
    print("uT =", uT)
    blynk.virtual_write(4, uT)
def auto_reset():
    print("auto reset")
    machine.reset()


timer.set_interval(1, blink_led)
timer.set_interval(5, print_uptime)
timer.set_interval(3660, auto_reset)

try:
    while True:
        gc.collect()
        blynk.run()
        timer.run()
        
except KeyboardInterrupt:
    print("Keyboard Interrupted")
except:
    print('error, reset')
    machine.reset()

