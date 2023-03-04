import time
import globals as g

def checkPumpEfi(t_set: float, t_accual: float, offset: int):
        interval1=60
        interval2=120
        accualTime = time.time()
        #print('JEstem w funkcji checkPumpEfi')
        #print('Aktualny czas:',accualTime)
        #print('acTimePLusInterwal:', g.acTimePLusInterwal)
        #print('accualTime - acTimePLusInterwal:',accualTime-g.acTimePLusInterwal)
        #print('drukuje typ zmiennej: t_set',type(t_set))
        #print('drukuje typ zmiennej: t_accual',type(t_accual))
        #print('drukuje typ zmiennej: offset',type(offset))
        #print('drukuje typ zmiennej: pumpEfi',type(g.pumpEfi))
        if accualTime >g.acTimePLusInterwal + interval1:
            #print('Interwal doliczyl do zadanej wartosci nastepuje triger')
            g.acTimePLusInterwal=accualTime
            
            if t_accual > (t_set + offset) and g.pumpEfi >= 0:
                #print('Interwal doliczyl do zadanej wartosci nastepuje dekrementacja acTimePLusInterwal', g.acTimePLusInterwal)
                g.pumpEfi=g.pumpEfi-1
            elif t_accual < (t_set - offset) and g.pumpEfi < 7:
                #print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', g.acTimePLusInterwal)
                g.pumpEfi=g.pumpEfi+1
        
        #print("------------>>>>>>>>jestem w funkcji 'checkPumpEfi' wyswietlam dane t_set:",t_set, 't_accual:', t_accual, 'Wydajnosc pompy:', g.pumpEfi, 'offset:', offset)
        
        