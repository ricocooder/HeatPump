
import RPi.GPIO as GPIO
import time
import globals as g


def setOutputs(state, temp, pumpEfi):
        SleepTime = 2
        interval1=60
        interval2=120
        BaseEfiInPercent = 100/7
        GPIO.setmode(GPIO.BCM)
        pins = [26,5,6,12,25,24,23,22]
        GPIO.setup(pins[0], GPIO.OUT)
        GPIO.setup(pins[1], GPIO.OUT)
        GPIO.setup(pins[2], GPIO.OUT)
        GPIO.setup(pins[3], GPIO.OUT)
        GPIO.setup(pins[4], GPIO.OUT)
        GPIO.setup(pins[5], GPIO.OUT)
        GPIO.setup(pins[6], GPIO.OUT)
        GPIO.setup(pins[7], GPIO.OUT)
        accualTime = time.time()

        if state == True:
            GPIO.output(pins[3], GPIO.HIGH)

        else:
           GPIO.output(pins[3], GPIO.LOW)
           
        if g.heatObject == 2:
            GPIO.output(pins[4], GPIO.HIGH)

        else:
           GPIO.output(pins[4], GPIO.LOW)
           
        
        if pumpEfi==0 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi==1 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 2 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 3 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 4 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 5 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 6 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 7 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        else:
            BaseEfiInPercent = 0
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
           
        
        return round(BaseEfiInPercent,1)