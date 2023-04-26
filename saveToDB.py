import sqlite3
import sys
import globals as g

def checkValues(dif):
    if abs(g.readTemp[0] - g.readTempTemp[0])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[0], g.readTempTemp[0]: ", g.readTemp[0], g.readTempTemp[0])
        log_values()
        saveTempData()
    if abs(g.readTemp[1] - g.readTempTemp[1])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[1], g.readTempTemp[1]: ", g.readTemp[1], g.readTempTemp[1])
        log_values()
        saveTempData()
    if abs(g.readTemp[2] - g.readTempTemp[2])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[2], g.readTempTemp[2]: ", g.readTemp[2], g.readTempTemp[2])
        log_values()
        saveTempData()
    if abs(g.pumpV - g.pumpVtemp)>=dif:
        print("Wykryto roznice pomiedzy g.pumpV, g.pumpVtemp: ", g.pumpV, g.pumpVtemp)
        log_values()
        saveTempData()
    if abs(g.pumpI - g.pumpItemp)>=dif:
        print("Wykryto roznice pomiedzy g.pumpI, g.pumpItemp: ", g.pumpI, g.pumpItemp)
        log_values()
        saveTempData()
    if abs(g.BaseEfiInPercent - g.BaseEfiInPercentTemp)>=dif:
        print("Wykryto roznice pomiedzy g.BaseEfiInPercent, g.BaseEfiInPercentTemp: ", g.BaseEfiInPercent, g.BaseEfiInPercentTemp)
        log_values()
        saveTempData()

def log_values():
	conn=sqlite3.connect('/home/pi/Documents/HeatPump/myDB.db')  #It is important to provide an
							     #absolute path to the database
							     #file, otherwise Cron won't be
							     #able to find it!
	# For the time-related code (record timestamps and time-date calculations) to work 
	# correctly, it is important to ensure that your Raspberry Pi is set to UTC.
	# This is done by default!
	# In general, servers are assumed to be in UTC.
	curs=conn.cursor()
	curs.execute("""INSERT INTO temp1 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[0]))
	curs.execute("""INSERT INTO temp2 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[1]))
	curs.execute("""INSERT INTO temp3 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[2]))
	curs.execute("""INSERT INTO volt values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.pumpV))
	curs.execute("""INSERT INTO cur values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.pumpI))
	curs.execute("""INSERT INTO efi values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.BaseEfiInPercent))
	
	conn.commit()
	conn.close()
	
def saveTempData():
        print("Aktualizuje g.readTempTemp[0] = g.readTemp[0] nowa wartoscia", g.readTempTemp[0], g.readTemp[0])        
        g.readTempTemp[0] = g.readTemp[0]
        print("Aktualizuje g.readTempTemp[1] = g.readTemp[1] nowa wartoscia", g.readTempTemp[1], g.readTemp[1])
        g.readTempTemp[1] = g.readTemp[1]
        print("Aktualizuje g.readTempTemp[2] = g.readTemp[2] nowa wartoscia", g.readTempTemp[2], g.readTemp[2])
        g.readTempTemp[2] = g.readTemp[2]
        print("Aktualizuje g.pumpVtemp = g.pumpV nowa wartoscia", g.pumpVtemp, g.pumpV)
        g.pumpVtemp = g.pumpV
        print("Aktualizuje g.pumpItemp = g.pumpI nowa wartoscia", g.pumpItemp, g.pumpI)
        g.pumpItemp = g.pumpI
        print("Aktualizuje g.BaseEfiInPercentTemp = g.BaseEfiInPercent nowa wartoscia", g.BaseEfiInPercentTemp, g.BaseEfiInPercent)
        g.BaseEfiInPercentTemp = g.BaseEfiInPercent
# If you don't have a sensor but still wish to run this program, comment out all the 
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
# import random
# humidity = random.randint(1,100)
# temperature = random.randint(10,30)
# if humidity is not None and temperature is not None:
# 	log_values("1", temperature, humidity)	
# else:
# 	log_values("1", -999, -999)