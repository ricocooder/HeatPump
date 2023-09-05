import time
import datetime as d
import globals as g

def checkPumpEfi(t_set: float, t_accual: float, offset: int, interval: int, heatObject: int):
    print(t_set, t_accual, offset[heatObject], interval[heatObject])
    accualTime = time.time()
    if g.pumpMode == 'auto':
        if accualTime >g.acTimePLusInterwal + interval[heatObject]:
            g.acTimePLusInterwal=accualTime
            if t_accual > (t_set + float(offset[heatObject])) and g.pumpEfi > 0:
                g.pumpEfi-=1
            elif t_accual < (t_set - float(offset[heatObject])) and g.pumpEfi < 7:
                g.pumpEfi+=1
        #logika pracy pompy latem
        if g.sezon == 'Lato':
            actualTime = d.datetime.now()
            actualHour = actualTime.hour
            dayOfWeek = actualTime.today().weekday()
            print('aktualnie wybrany sezon: ', g.sezon, ' Aktualna godzina: ', actualHour, ' Dzien tygodnia: ', dayOfWeek+1, 'watrosc komurki w tablicy: ', g.godzina[actualHour][dayOfWeek+1])
            if g.godzina[actualHour][dayOfWeek+1] == "ON":
                print('pompa pracuje')
                g.heatObject = 1
                # g.pumpEfi=7
            else:
                print('pompa nie pracuje')
                g.heatObject = 0
                
        #logika pracy pompy zima    
        else:
            print('jestes w logice dla zima',g.setTemp[1], g.pumpTempOfset[1], g.readTemp[g.sensorIndexList[1]])
            #jesli temp zadana boiler + offset boiler jest mniejsza nie odczytana na boilerze
            if g.setTemp[1]-g.pumpTempOfset[1] > g.readTemp[g.sensorIndexList[1]]:
                #grzanie boilera - przesterowanie zaworu ustawienie pompy na maxa?
                g.heatObject = 1
                # g.pumpEfi=7
            #jesli temperatura zadana boiler jest wieksza temp odczytana 
            elif g.setTemp[1] < g.readTemp[g.sensorIndexList[1]]:
            # elif g.setTemp[1] < g.readTemp[1] and g.setTemp[2] > g.readTemp[2]:
            #jesli temperatura zadana boiler plus offset boiler jest wieksza/rowna temp odczytana boiler            
            # elif g.setTemp[1] + g.pumpTempOfset[1] <= g.readTemp[1]:
                #grzanie podlogowki ustawiam pompe na "srodkowy" tryb
                g.heatObject = 2
                # g.pumpEfi=2
            else:
                #wylaczam pompe
                g.heatObject = 0
                print('pompa wylaczona')
        