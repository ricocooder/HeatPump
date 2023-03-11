
import RPi.GPIO as GPIO
import time
import globals as g


def setOutputs(heatObject, temp, pumpEfi):
        BaseEfiInPercent = 100/7
        GPIO.setmode(GPIO.BCM)
        pins = g.pins
        GPIO.setup(pins[0], GPIO.OUT)
        GPIO.setup(pins[1], GPIO.OUT)
        GPIO.setup(pins[2], GPIO.OUT)
        GPIO.setup(pins[3], GPIO.OUT)
        GPIO.setup(pins[4], GPIO.OUT)
        GPIO.setup(pins[5], GPIO.OUT)
        GPIO.setup(pins[6], GPIO.OUT)
        GPIO.setup(pins[7], GPIO.OUT)
        accualTime = time.time()

        if heatObject != 0:
            GPIO.output(pins[3], GPIO.HIGH)
            g.tempPins[3] = 0

        else:
           GPIO.output(pins[3], GPIO.LOW)
           g.tempPins[3] = 1
           
        if g.heatObject == 2:
            GPIO.output(pins[4], GPIO.HIGH)
            g.tempPins[4] = 0

        else:
           GPIO.output(pins[4], GPIO.LOW)
           g.tempPins[4] = 1
           
        
        if pumpEfi==0 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[1], GPIO.LOW)
            g.tempPins[1] = 1
            GPIO.output(pins[2], GPIO.LOW)
            g.tempPins[2] = 1
        elif pumpEfi==1 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[1], GPIO.LOW)
            g.tempPins[1] = 1
            GPIO.output(pins[2], GPIO.HIGH)
            g.tempPins[2] = 0
        elif pumpEfi == 2 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[1], GPIO.HIGH)
            g.tempPins[1] = 0
            GPIO.output(pins[2], GPIO.LOW)
            g.tempPins[2] = 1
        elif pumpEfi == 3 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            g.tempPins[0] = 0
            GPIO.output(pins[1], GPIO.LOW)
            g.tempPins[1] = 1
            GPIO.output(pins[2], GPIO.LOW)
            g.tempPins[2] = 1
        elif pumpEfi == 4 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[1], GPIO.HIGH)
            g.tempPins[1] = 0
            GPIO.output(pins[2], GPIO.HIGH)
            g.tempPins[2] = 0
        elif pumpEfi == 5 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            g.tempPins[0] = 0
            GPIO.output(pins[1], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[2], GPIO.HIGH)
            g.tempPins[2] = 0
        elif pumpEfi == 6 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            g.tempPins[0] = 0
            GPIO.output(pins[1], GPIO.HIGH)
            g.tempPins[1] = 0
            GPIO.output(pins[2], GPIO.LOW)
            g.tempPins[2] = 1
        elif pumpEfi == 7 and heatObject != 0:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            g.tempPins[0] = 0
            GPIO.output(pins[1], GPIO.HIGH)
            g.tempPins[1] = 0
            GPIO.output(pins[2], GPIO.HIGH)
            g.tempPins[2] = 0
        else:
            BaseEfiInPercent = 0
            GPIO.output(pins[0], GPIO.LOW)
            g.tempPins[0] = 1
            GPIO.output(pins[1], GPIO.LOW)
            g.tempPins[1] = 1
            GPIO.output(pins[2], GPIO.LOW)
            g.tempPins[2] = 1
           
        
        return round(BaseEfiInPercent,1)