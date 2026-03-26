import sqlite3
import sys
import globals as g

def checkValues(dif):
    if abs(g.readTemp[g.sensorIndexList[0]] - g.readTempTemp[0])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[g.sensorIndexList[0]], g.readTempTemp[0]: ", g.readTemp[g.sensorIndexList[0]], g.readTempTemp[0])
        log_values()
        saveTempData()
    if abs(g.readTemp[g.sensorIndexList[1]] - g.readTempTemp[1])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[g.sensorIndexList[1]], g.readTempTemp[1]: ", g.readTemp[g.sensorIndexList[1]], g.readTempTemp[1])
        log_values()
        saveTempData()
    if abs(g.readTemp[g.sensorIndexList[2]] - g.readTempTemp[2])>=dif:
        print("Wykryto roznice pomiedzy g.readTemp[g.sensorIndexList[2]], g.readTempTemp[2]: ", g.readTemp[g.sensorIndexList[2]], g.readTempTemp[2])
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
	conn=sqlite3.connect('/home/pi/Documents/HeatPump/myDB.db')
	curs=conn.cursor()
	curs.execute("""INSERT INTO temp1 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[g.sensorIndexList[0]]))
	curs.execute("""INSERT INTO temp2 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[g.sensorIndexList[1]]))
	curs.execute("""INSERT INTO temp3 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.readTemp[g.sensorIndexList[2]]))
	curs.execute("""INSERT INTO volt values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.pumpV))
	curs.execute("""INSERT INTO cur values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.pumpI))
	curs.execute("""INSERT INTO efi values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",g.BaseEfiInPercent))
	
	conn.commit()
	conn.close()
	
def saveTempData():
        print("Aktualizuje g.readTempTemp[0] = g.readTemp[g.sensorIndexList[0]] nowa wartoscia", g.readTempTemp[0], g.readTemp[g.sensorIndexList[0]])        
        g.readTempTemp[0] = g.readTemp[g.sensorIndexList[0]]
        print("Aktualizuje g.readTempTemp[1] = g.readTemp[g.sensorIndexList[1]] nowa wartoscia", g.readTempTemp[1], g.readTemp[g.sensorIndexList[1]])
        g.readTempTemp[1] = g.readTemp[g.sensorIndexList[1]]
        print("Aktualizuje g.readTempTemp[2] = g.readTemp[g.sensorIndexList[2]] nowa wartoscia", g.readTempTemp[2], g.readTemp[g.sensorIndexList[2]])
        g.readTempTemp[2] = g.readTemp[g.sensorIndexList[2]]
        print("Aktualizuje g.pumpVtemp = g.pumpV nowa wartoscia", g.pumpVtemp, g.pumpV)
        g.pumpVtemp = g.pumpV
        print("Aktualizuje g.pumpItemp = g.pumpI nowa wartoscia", g.pumpItemp, g.pumpI)
        g.pumpItemp = g.pumpI
        print("Aktualizuje g.BaseEfiInPercentTemp = g.BaseEfiInPercent nowa wartoscia", g.BaseEfiInPercentTemp, g.BaseEfiInPercent)
        g.BaseEfiInPercentTemp = g.BaseEfiInPercent