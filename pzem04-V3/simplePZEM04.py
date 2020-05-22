'''
Micropython in esp32 simple example for use PZEM04t V3 in default modbus address 0xF8
whithout modbus library. Use UART1 or UART2.
2020-05-22
Jaume Nogues, jnogues@gmail.com
'''

from machine import UART
import time, struct
uart = UART(2, 9600, tx=13, rx=14) #UART2, tx=gpio13 rx=gpio14

count=0

def read_measures():
    signed=True
    uart.write(b'\xF8\x04\x00\x00\x00\x0A\x64\x64')#read all raw measures
    time.sleep(0.1)
    payload = uart.read()
    payload = payload[3:-2]
    response_quantity = int(len(payload) / 2)
    fmt = '>' + (('h' if signed else 'H') * response_quantity)
    return struct.unpack(fmt, payload)

def reset_energy():
    uart.write(b'\xF8\x42\xC2\x41')#reset energy


while True:
    try:
        #read all measures in one time
        all_measures = read_measures()
        print(all_measures)
        #split and print measues
        voltage = all_measures[0]/10.0
        print('U = ' + str(voltage) + ' V')
        current = ((all_measures[2]<<16) |  (all_measures[1]))/1000.0
        print('I = ' + str(current) + ' A')
        power = ((all_measures[4]<<16) |  (all_measures[3]))/10.0
        print('P = ' + str(power) + ' W')
        energy = ((all_measures[6]<<16) |  (all_measures[5]))/1000.0
        print('E = ' + str(energy) + ' kWh')
        freq = all_measures[7]/10.0
        print('freq = ' + str(freq) + ' Hz')
        pf = all_measures[8]/10.0
        print('power factor = ' + str(pf))
    except:
        #something wrong
        print('pzem04 reading error')
        
    #delay some seconds
    time.sleep(5)


