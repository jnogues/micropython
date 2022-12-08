from machine import Pin, freq
import time


freq(160000000)
print("Comencem....")
print("machine freq: ", freq()/1000_000 , "MHz")

scan_start = time.ticks_ms()

task1_start = time.ticks_ms()
task1_interval = 50

task2_start = time.ticks_ms()
task2_interval = 200

task3_start = time.ticks_ms()
task3_interval = 300

task4_start = time.ticks_ms()
task4_interval = 400

comptador = 0

led16 = Pin(16, Pin.OUT)
led13 = Pin(13, Pin.OUT)
led0 = Pin(0, Pin.OUT)
led2 = Pin(2, Pin.OUT)

#Definició de les tasques
def task1():
    led16.value (not led16.value())
    
def task2():
    led13.value (not led13.value())

def task3():
    led0.value (not led0.value())
    
def task4():
    led2.value (not led2.value())


#main loop
while True:
    if time.ticks_ms()help - task1_start >= task1_interval:
        task1()
        task1_start = time.ticks_ms()
    if time.ticks_ms() - task2_start >= task2_interval:
        task2()
        task2_start = time.ticks_ms()
    if time.ticks_ms() - task3_start >= task3_interval:
        task3()
        task3_start = time.ticks_ms()
    if time.ticks_ms() - task4_start >= task4_interval:
        task4()
        task4_start = time.ticks_ms()
        
    comptador = comptador + 1
    if comptador == 100_000:
        print( (time.ticks_ms() - scan_start)/1000 , "s" )
        scan_start = time.ticks_ms()
        #print("*")
        comptador = 0
