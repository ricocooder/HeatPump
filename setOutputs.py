
import RPi.GPIO as GPIO
import time
import globals as g


def setOutputs(heatObject, temp, pumpEfi):
        BaseEfiInPercent = 100/7
        g.pumpI = 16.0/7
        GPIO.setmode(GPIO.BCM)
        pins = g.pins
        GPIO.setup(pins[0], GPIO.OUT)#Sterowanie pompy1 (NC)
        GPIO.setup(pins[1], GPIO.OUT)#Sterowanie pompy2 (NC)
        GPIO.setup(pins[2], GPIO.OUT)#Sterowanie pompy3 (NC)
        GPIO.setup(pins[3], GPIO.OUT)#Zawor trojdrogowy (NO)
        GPIO.setup(pins[4], GPIO.OUT)#sterownik piec (NC)
        GPIO.setup(pins[5], GPIO.OUT)#zal/wyl 24V (NC)
        GPIO.setup(pins[6], GPIO.OUT)#pompa obiegowa (NC)
        GPIO.setup(pins[7], GPIO.OUT)
        accualTime = time.time()
        if g.pumpMode == 'auto':
            if pumpEfi < 1 or g.heatObject != 2:
                GPIO.output(pins[6], GPIO.HIGH)
                g.tempPins[6] = 1

            else:
                GPIO.output(pins[6], GPIO.LOW)
                g.tempPins[6] = 0          
            
            
            if g.heatObject == 1:
                GPIO.output(pins[3], GPIO.HIGH)
                g.tempPins[3] = 1

            else:
                GPIO.output(pins[3], GPIO.LOW)
                g.tempPins[3] = 0        
            
            
            if g.heatObject == 0:
                GPIO.output(pins[4], GPIO.LOW)
                g.tempPins[4] = 0

            else:
                GPIO.output(pins[4], GPIO.HIGH)
                g.tempPins[4] = 1
            
            
            if pumpEfi==7 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 235
                GPIO.output(pins[0], GPIO.LOW)
                g.tempPins[0] = 0
                GPIO.output(pins[1], GPIO.LOW)
                g.tempPins[1] = 0
                GPIO.output(pins[2], GPIO.LOW)
                g.tempPins[2] = 0
            elif pumpEfi==6 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 234
                GPIO.output(pins[0], GPIO.LOW)
                g.tempPins[0] = 0
                GPIO.output(pins[1], GPIO.LOW)
                g.tempPins[1] = 0
                GPIO.output(pins[2], GPIO.HIGH)
                g.tempPins[2] = 1
            elif pumpEfi == 5 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 233
                GPIO.output(pins[0], GPIO.LOW)
                g.tempPins[0] = 0
                GPIO.output(pins[1], GPIO.HIGH)
                g.tempPins[1] = 1
                GPIO.output(pins[2], GPIO.LOW)
                g.tempPins[2] = 0
            elif pumpEfi == 4 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 232
                GPIO.output(pins[0], GPIO.HIGH)
                g.tempPins[0] = 1
                GPIO.output(pins[1], GPIO.LOW)
                g.tempPins[1] = 0
                GPIO.output(pins[2], GPIO.LOW)
                g.tempPins[2] = 0
            elif pumpEfi == 3 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 231
                GPIO.output(pins[0], GPIO.LOW)
                g.tempPins[0] = 0
                GPIO.output(pins[1], GPIO.HIGH)
                g.tempPins[1] = 1
                GPIO.output(pins[2], GPIO.HIGH)
                g.tempPins[2] = 1
            elif pumpEfi == 2 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 230
                GPIO.output(pins[0], GPIO.HIGH)
                g.tempPins[0] = 1
                GPIO.output(pins[1], GPIO.LOW)
                g.tempPins[0] = 0
                GPIO.output(pins[2], GPIO.HIGH)
                g.tempPins[2] = 1
            elif pumpEfi == 1 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 229
                GPIO.output(pins[0], GPIO.HIGH)
                g.tempPins[0] = 1
                GPIO.output(pins[1], GPIO.HIGH)
                g.tempPins[1] = 1
                GPIO.output(pins[2], GPIO.LOW)
                g.tempPins[2] = 0
            elif pumpEfi == 0 and heatObject != 0:
                BaseEfiInPercent = BaseEfiInPercent*pumpEfi
                g.pumpI=round(g.pumpI*pumpEfi,2)
                g.pumpV = 228
                GPIO.output(pins[0], GPIO.HIGH)
                g.tempPins[0] = 1
                GPIO.output(pins[1], GPIO.HIGH)
                g.tempPins[1] = 1
                GPIO.output(pins[2], GPIO.HIGH)
                g.tempPins[2] = 1
            else:
                BaseEfiInPercent = 0
                g.pumpI=round(g.pumpI*pumpEfi,2)
                GPIO.output(pins[0], GPIO.HIGH)
                g.tempPins[0] = 1
                GPIO.output(pins[1], GPIO.HIGH)
                g.tempPins[1] = 1
                GPIO.output(pins[2], GPIO.HIGH)
                g.tempPins[2] = 1
        else:
            # for pin in g.tempPins:
            #     if g.tempPins[pin] == 1:
            #         GPIO.output(pins[pin], GPIO.HIGH)
            #     else:
            #         GPIO.output(pins[pin], GPIO.LOW)
            if g.tempPins[0] == 1:
                GPIO.output(pins[0], GPIO.HIGH)
            else:
                GPIO.output(pins[0], GPIO.LOW)

            if g.tempPins[1] == 1:
                GPIO.output(pins[1], GPIO.HIGH)
            else:
                GPIO.output(pins[1], GPIO.LOW)

            if g.tempPins[2] == 1:
                GPIO.output(pins[2], GPIO.HIGH)
            else:
                GPIO.output(pins[2], GPIO.LOW)

            if g.tempPins[3] == 1:
                GPIO.output(pins[3], GPIO.HIGH)
            else:
                GPIO.output(pins[3], GPIO.LOW)

            if g.tempPins[4] == 1:
                GPIO.output(pins[4], GPIO.HIGH)
            else:
                GPIO.output(pins[4], GPIO.LOW)

            if g.tempPins[5] == 1:
                GPIO.output(pins[5], GPIO.HIGH)
            else:
                GPIO.output(pins[5], GPIO.LOW)

            if g.tempPins[6] == 1:
                GPIO.output(pins[6], GPIO.HIGH)
            else:
                GPIO.output(pins[6], GPIO.LOW)
                
            if g.tempPins[7] == 1:
                GPIO.output(pins[7], GPIO.HIGH)
            else:
                GPIO.output(pins[7], GPIO.LOW)


           
        
        return round(BaseEfiInPercent,1)