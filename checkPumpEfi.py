import time
import datetime as d
import globals as g

def checkPumpEfi(t_set: float, t_accual: float, offset: int, interval: int, heatObject: int):
    print(t_set, t_accual, offset[heatObject], interval[heatObject])
    accualTime = time.time()
    if accualTime >g.acTimePLusInterwal + interval[heatObject]:
        g.acTimePLusInterwal=accualTime
        if t_accual > (t_set + float(offset[heatObject])) and g.pumpEfi >= 0:
            g.pumpEfi=g.pumpEfi-1
        elif t_accual < (t_set - float(offset[heatObject])) and g.pumpEfi < 7:
            g.pumpEfi=g.pumpEfi+1
    #logika pracy pompy latem
    if g.sezon == 'Lato':
        actualTime = d.datetime.now()
        actualHour = actualTime.hour
        dayOfWeek = actualTime.today().weekday()
        print(g.sezon, actualHour, dayOfWeek)
        if dayOfWeek > 5:
            #ustalam harmonogram od poniedzialku do piatku dni tygodnie to zakres 0-6
            print('zwracam dzien tygodnia', dayOfWeek)
            if actualHour >=7 and < 9 or actualHour >= 18 and < 22:
                #wieczorne grzanie
                print('wieczoren grzanie')
        else:
            #pozostale dni tygodnia czyli sobota i niedziela
            print('zwracam dzien tygodnia', dayOfWeek)
            if actualHour >= 7 and actualHour < 22:
                #ustawiam harmonogram od 7 do 22 godziny w niedziele i sobote
                print('praca od 7 do 22')
            else:
                #wylaczam pompe
                print('pompa wylaczona')
            
    #logika pracy pompy zima    
    else:
        print("else")
        