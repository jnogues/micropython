import machine
from machine import Pin
import time
import uasyncio
import gc
import network
from umqtt.simple import MQTTClient
import ujson
import onewire, ds18x20


led = Pin(2, Pin.OUT)
wifi_OK = 0
broker_OK = 0
t_ds18b20 = 0

#tasca 1
async def blinkLed():
    while True:

        led.off() #led.value(0)
        await uasyncio.sleep(0.1)
        led.on() #led.value(1)
        await uasyncio.sleep(10)

async def do_connect():
    global wifi_OK
    wifi_OK = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    #wlan.disconnect()#?? millor no
    await uasyncio.sleep(1)
    wlan.active(True)
    
    while True:
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('elMeuWifi', 'elMeuPass')
            timeout = 0
            while (not wlan.isconnected() and timeout < 5):
                print(5 - timeout)
                timeout = timeout + 1
                await uasyncio.sleep(2)
            if(wlan.isconnected()):
                print('connected')
                wifi_OK = 1
            else:
                print('not connected')
                wifi_OK = 0
        if (wlan.isconnected()):
            wifi_OK = 1
            #print('network config:', wlan.ifconfig())
        await uasyncio.sleep(10)


async def connect_broker():
    global wifi_OK
    global broker_OK
    uptime_broker = 0
    print("connecting to broker")
    while True:
        if(broker_OK == 0 and wifi_OK == 1):
            try:            
                client.connect()
                print("broker connected")
                client.subscribe('/ds18b20node/in') # Subscribing to particular topic
                broker_OK = 1
            except Exception as e:
                print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
                #client.disconnect()
                broker_OK = 0
                #sys.exit()
        if(broker_OK ==1 and wifi_OK == 1):
            try:
                client.publish("/ds18b20node", "{}".format(uptime_broker), 0)
                #print("broker OK")
                broker_OK = 1
            except:    
                print("broker KO")
                broker_OK = 0
        
        #print("broker = ", uptime_broker)
        uptime_broker += 1
        await uasyncio.sleep(30)

async def check_incomming_msg():
    global wifi_OK
    global broker_OK
    while True:
        if(broker_OK ==1 and wifi_OK == 1):
            try:
                client.check_msg()                  # non blocking function
            except :
                print("error checking incomming")
                broker_OK = 0
                #client.disconnect()
        await uasyncio.sleep(0.3)


def cb(topic, msg):                             # Callback function
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    recieved_data = str(msg,'utf-8')            #   Recieving Data
    if recieved_data=="0":
        #led.value(0)
        print("OFF")
    if recieved_data=="1":
        #led.value(1)
        print("ON")

async def send_data():
    global broker_OK
    global wifi_OK
    global t_ds18b20
    while True:
        if(broker_OK ==1 and wifi_OK == 1):
            dictPayload={}
            uT = time.ticks_ms()//1000
            dictPayload["node"] = 'nodeMCUds18b20'
            dictPayload["uT"] = uT
            dictPayload["temp"] = t_ds18b20
            
            payload=ujson.dumps(dictPayload)
            #print(payload)
            
            try:
                client.publish("/ds18b20node/state", payload, 0)
                print("publish OK")
                broker_OK = 1
            except:    
                print("publish KO")
                broker_OK = 0
        await uasyncio.sleep(10)


async def measure_temperature():
    global t_ds18b20
    t = [0, 0, 0, 0, 0]
    comptador = 0
    ds_pin = machine.Pin(13)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    while True:
        try:    
            roms = ds_sensor.scan()
            #print('Found DS devices: ', roms)#debug
            for rom in roms:
                ds_sensor.write_scratch(rom,  b'\x00\x00\x5f')
                #9  bits b'\x00\x00\x1f
                #10 bits b'\x00\x00\x3f'
                #11 bits b'\x00\x00\x5f'
                #12 bits b'\x00\x00\x7f'    
            ds_sensor.convert_temp()
            await uasyncio.sleep(1)
            for rom in roms:
                #print(rom)
                t[comptador] = ds_sensor.read_temp(rom)
                #print("t[",comptador,"] = ",  t[comptador])
                comptador = comptador + 1
                if comptador == 5:
                    comptador = 0
                
        except:
            print("error")
            t[comptador] = 0
            
        #print(t)
        t_ds18b20 = round(median(t), 1)
        print(t_ds18b20)    
        await uasyncio.sleep(10)
 
def median(data):
    data = sorted(data)
    n = len(data)
    if n % 2 == 1:
        return data[n//2]
    else:
        i = n//2
        return (data[i - 1] + data[i])/2


async def main():
    counter = 0
    timestamp = 0
    print("Comencem main!!!!!")
    uasyncio.create_task(blinkLed())
    uasyncio.create_task(do_connect())
    uasyncio.create_task(connect_broker())
    uasyncio.create_task(check_incomming_msg())
    uasyncio.create_task(send_data())
    uasyncio.create_task(measure_temperature())
    
    #loop principal un cop iniciades les tasques
    while True:
        counter = counter + 1
        #print("counter = ", counter)
        timestamp = time.ticks_ms()/1000
        #print ("timeStamp =",timestamp)
        gc.collect()
        #print("mem free: ", gc.mem_free())
        await uasyncio.sleep(5)

machine.freq(160000000)
print("machine freq: ", machine.freq())
client = MQTTClient('esp8266MP2', 'test.mosquitto.org', keepalive=30)
#client = MQTTClient('esp8266parlament', 'test.mosquitto.org')
#client = MQTTClient('esp8266MP', 'test.mosquitto.org', user='fulano', password='1234')
client.DEBUG = True
client.set_callback(cb)      # Callback function 

try:
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()
