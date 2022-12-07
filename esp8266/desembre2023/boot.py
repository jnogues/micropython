# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(False)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

import uos
from time import sleep
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()
print("mem free: ", gc.mem_free())

sleep(4)
print("@")
import main
