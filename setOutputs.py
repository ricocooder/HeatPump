
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
        # print('Aktualny czas:',accualTime)
        
        # print('acTimePLusInterwal:', g.acTimePLusInterwal)
        # print('accualTime - acTimePLusInterwal:',accualTime-g.acTimePLusInterwal)
        
        # if accualTime >acTimePLusInterwal +interval1:
        #     print('Interwal doliczyl do zadanej wartosci nastepuje triger')
        #     acTimePLusInterwal=accualTime
        #     print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', acTimePLusInterwal)
        # print("------------>>>>>>>>jestem w funkcji 'setOutputs' wyswietlam dane state:",state, 'Temp:', temp, 'Wydajnosc pompy:', pumpEfi)
        
        # if state and temp < 25.0:
        #     print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa woda urzytkowa - PonWU.jpg ")
            # pick1=os.path.join(app.config["UPLOAD_FOLDER"], "PonWU.jpg")
        # if state and temp > 25.0 and temp < 30.0:
        #     print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa centralne ogrzewanie PonCO.jpg ")
            # pick1=os.path.join(app.config["UPLOAD_FOLDER"], "PonCO.jpg")
        # if state==False:
        #     print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa wylaczona P_off.jpg ")
            # pick1=os.path.join(app.config["UPLOAD_FOLDER"], "P_off.jpg")
            
        if state == True:
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek state == True", state)
            GPIO.output(pins[3], GPIO.HIGH)

        else:
           GPIO.output(pins[3], GPIO.LOW)
        
        if pumpEfi==0 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 0")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi==1 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 1")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 2 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 2")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 3 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 3")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 4 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 4")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 5 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 5")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 6 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 6")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 7 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            #print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 7")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        else:
            BaseEfiInPercent = 0
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
           
        
        return round(BaseEfiInPercent,1)