import time
import glob
from flask import flash
import globals as g

base_dir = '/sys/bus/w1/devices/'
# device_number = glob.glob(base_dir+'w1_bus_master1/w1_master_slave_count')

# with open(device_number, 'r') as r:
#      print(r)

#device_path = glob.glob(base_dir + '28*')[0] #get file path of sensor
#rom = device_path.split('/')[-1] #get rom name
# print('naliczylem ', device_number, ' urzadzen w tablicy')
def read_temp_raw(sensor_number):
    device_path = glob.glob(base_dir + '28*')[sensor_number]
    rom = device_path.split('/')[-1]
    with open(device_path +'/w1_slave','r') as f:
        valid, temp = f.readlines()
    return valid, temp
 
def read_temp():
    tempfile = open('/sys/bus/w1/devices/w1_bus_master1/w1_master_slave_count')
    g.tempSensFoundNumber = int(tempfile.read())
    tempfile.close()
    # print('Znalziono',g.tempSensFoundNumber,'podlaczonych czujnikow')
    # print(type(int(g.tempSensFoundNumber)))
    for x in range(int(g.tempSensFoundNumber)):
        # print('przypisuje wartosc dla',x, 'czujnika')


        valid, temp = read_temp_raw(x)

        while 'YES' not in valid:
            time.sleep(0.2)
            valid, temp = read_temp_raw()
            
        pos = temp.index('t=')
        if pos != -1:
            temp_string = temp[pos+2:]
            temp_c = float(temp_string)/1000.0 
            # print("odczyt temperatury z miejsca ", x,": ", temp_c)
            # setString = 'readTemp'+ str(x)
            # print(setString)
            g.readTemp[x]=round(temp_c, 1)
            # print('oraz g.readTemp[x]', g.readTemp[x])
            # return temp_c

