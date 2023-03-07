import time
import globals as g

def checkPumpEfi(t_set: float, t_accual: float, offset: int, interval: int):
    print(t_set, t_accual, offset, interval)
    accualTime = time.time()
    if accualTime >g.acTimePLusInterwal + interval:
        g.acTimePLusInterwal=accualTime
        if t_accual > (t_set + offset) and g.pumpEfi >= 0:
            g.pumpEfi=g.pumpEfi-1
        elif t_accual < (t_set - offset) and g.pumpEfi < 7:
            g.pumpEfi=g.pumpEfi+1