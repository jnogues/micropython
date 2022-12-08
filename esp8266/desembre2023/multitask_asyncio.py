from machine import Pin, freq
import time
import uasyncio
import gc


freq(160000000)
print("Comencem....")
print("machine freq: ", freq()/1000_000 , "MHz")
time.sleep(2)

led16 = Pin(16, Pin.OUT)
led13 = Pin(13, Pin.OUT)
led0 = Pin(0, Pin.OUT)
led2 = Pin(2, Pin.OUT)

#Definició de les tasques
async def task1():
    while True:
        led16.value (not led16.value())
        await uasyncio.sleep(0.05)
    
async def task2():
    while True:
        led13.value (not led13.value())
        await uasyncio.sleep(1)

async def task3():
    while True:
        led0.value (not led0.value())
        await uasyncio.sleep(1.2)
    
async def task4():
    while True:
        led2.value (not led2.value())
        await uasyncio.sleep(1.4)


#main loop
async def main():
    comptador = 0
    scan_start = time.ticks_ms()

    uasyncio.create_task(task1())
    uasyncio.create_task(task2())
    uasyncio.create_task(task3())
    uasyncio.create_task(task4())
    
    while True: 
        await uasyncio.sleep(5)
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        print("mem free: ", gc.mem_free())

try:
    uasyncio.run(main())
except KeyboardInterrupt:
    print("Keyboard Interrupted")
except asyncio.TimeoutError:
    print("Time out")
finally:
    uasyncio.new_event_loop()
