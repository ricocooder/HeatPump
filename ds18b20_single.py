import os
import glob
import time
import RPi.GPIO as GPIO
import time as t

#these tow lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

base_dir = '/sys/bus/w1/devices/'
device_path = glob.glob(base_dir + '28*')[0] #get file path of sensor
rom = device_path.split('/')[-1] #get rom name

def read_temp_raw():
    with open(device_path +'/w1_slave','r') as f:
        valid, temp = f.readlines()
    return valid, temp
 
def read_temp():
    valid, temp = read_temp_raw()

    while 'YES' not in valid:
        time.sleep(0.2)
        valid, temp = read_temp_raw()

    pos = temp.index('t=')
    if pos != -1:
        #read the temperature .
        temp_string = temp[pos+2:]
        temp_c = float(temp_string)/1000.0 
        temp_f = temp_c * (9.0 / 5.0) + 32.0
        return temp_c, temp_f
 
print(' ROM: '+ rom)

while True:
    c, f = read_temp()
    print('C={:,.3f} F={:,.3f}'.format(c, f))
    if c >= 24:
           GPIO.output(26, GPIO.HIGH)
    else:
        GPIO.output(26, GPIO.LOW)
    if c >= 25:
           GPIO.output(5, GPIO.HIGH)
    else:
        GPIO.output(5, GPIO.LOW)
    if c >= 27:
           GPIO.output(6, GPIO.HIGH)
    else:
        GPIO.output(6, GPIO.LOW)
    if c >= 28:
           GPIO.output(12, GPIO.HIGH)
    else:
        GPIO.output(12, GPIO.LOW)
    if c >= 29:
           GPIO.output(25, GPIO.HIGH)
    else:
        GPIO.output(25, GPIO.LOW)
    if c >= 30:
           GPIO.output(24, GPIO.HIGH)
    else:
        GPIO.output(24, GPIO.LOW)
    if c >= 31:
           GPIO.output(23, GPIO.HIGH)
    else:
        GPIO.output(23, GPIO.LOW)
    if c >= 32:
           GPIO.output(22, GPIO.HIGH)
    else:
        GPIO.output(22, GPIO.LOW)
        
    time.sleep(1)
    
    
