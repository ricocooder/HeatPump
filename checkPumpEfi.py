import time
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