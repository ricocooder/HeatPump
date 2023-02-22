from flask import Flask, flash, render_template, request
import RPi.GPIO as GPIO
import time as t
import webbrowser
import time
import glob
import os

test = 0


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"]=pickFolder
mainState = True
acTimePLusInterwal=0
pumpEfi = 1
t1=21
to1="opis czujnika 1"
t2=22
to2="opis czujnika 2"
t3=23
to3="opis czujnika 3"
t4=24
to4="opis czujnika 4"
t5=25
to5="opis czujnika 5"
t6=26
to6="opis czujnika 6"
tz1 = 55.1
tzo1="boiler"
tz2=36
tzo2="ogrzewanie podłogowe"

base_dir = '/sys/bus/w1/devices/'
device_path = glob.glob(base_dir + '28*')[0] #get file path of sensor
rom = device_path.split('/')[-1] #get rom name



@app.route('/')
def hello_world():
    output = request.form.to_dict()
    global mainState
    global pumpEfi
    global tz1
    global tz2
    if request.method =='POST':
        if request.form.get('Save1')=='Save':
            try:
                tz1=float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrond input variable')
                print('error wrong variable')
        if request.form.get('Save2')=='Save':
            tz2=request.form['tempZad2']
        if request.form.get('Przycisk_1')=='Przycisk_1':
            if pumpEfi < 8:
                pumpEfi = pumpEfi + 1
            else:
                pumpEfi = 0
            print('-------->>>>>   Przycisk_1 zostal wcisneity pumpEfi = ', pumpEfi)
            print('-------->>>>>   Przycisk_1 zostal wcisneity')           
        if request.form.get('Przycisk_2')=='Przycisk_2':
            if pumpEfi >= 0:
                pumpEfi = pumpEfi - 1
            else:
                pumpEfi = 0
            print('-------->>>>>   Przycisk_2 zostal wcisneity pumpEfi = ', pumpEfi)
            print('-------->>>>>   Przycisk_2 zostal wcisneity')
        if request.form.get('Turn OFF Pump')=='Turn OFF Pump':
            mainState = False
            print('-------->>>>>   przycisk wylaczenia pompy zostal wcisniety')
        if request.form.get('Turn ON Pump')=='Turn ON Pump':
            print('-------->>>>>   przycisk wlaczenia pompy zostal wcisniety')
            mainState = True
    c, f = read_temp()
    pick1, BaseEfiInPercent = setOutputs(mainState, c, pumpEfi)
    return render_template("index.html", t1=c, to1=to1, t2=t2, to2=to2, t3=t3, to3=to3, t4=t4, to4=to4, t5=t5, to5=to5, t6=t6, to6=to6, tz1=tz1, tz2=tz2, tzo2=tzo2, image1=pick1, pump=BaseEfiInPercent, mainState=mainState)

@app.route("/result", methods = ["POST", "GET"])
def result():
    output = request.form.to_dict()
    global mainState
    global pumpEfi
    global tz1
    global tz2
    if request.method =='POST':
        if request.form.get('Save1')=='Save':
            try:
                tz1=float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrond input variable')
                print('error wrong variable')
        if request.form.get('Save2')=='Save':
            tz2=request.form['tempZad2']
        if request.form.get('Przycisk_1')=='Przycisk_1':
            if pumpEfi < 8:
                pumpEfi = pumpEfi + 1
            else:
                pumpEfi = 0
            print('-------->>>>>   Przycisk_1 zostal wcisneity pumpEfi = ', pumpEfi)
            print('-------->>>>>   Przycisk_1 zostal wcisneity')           
        if request.form.get('Przycisk_2')=='Przycisk_2':
            if pumpEfi >= 0:
                pumpEfi = pumpEfi - 1
            else:
                pumpEfi = 0
            print('-------->>>>>   Przycisk_2 zostal wcisneity pumpEfi = ', pumpEfi)
            print('-------->>>>>   Przycisk_2 zostal wcisneity')
        if request.form.get('Turn OFF Pump')=='Turn OFF Pump':
            mainState = False
            print('-------->>>>>   przycisk wylaczenia pompy zostal wcisniety')
        if request.form.get('Turn ON Pump')=='Turn ON Pump':
            print('-------->>>>>   przycisk wlaczenia pompy zostal wcisniety')
            mainState = True
    c, f = read_temp()
    pick1, BaseEfiInPercent = setOutputs(mainState, c, pumpEfi)
    checkPumpEfi(tz1, c, 5)
    return render_template("index.html", t1=c, to1=to1, t2=t2, to2=to2, t3=t3, to3=to3, t4=t4, to4=to4, t5=t5, to5=to5, t6=t6, to6=to6, tz1=tz1, tz2=tz2, tzo2=tzo2, image1=pick1, pump=BaseEfiInPercent, mainState=mainState)

def read_temp_raw():
    with open(device_path +'/w1_slave','r') as f:
        valid, temp = f.readlines()
    return valid, temp
 
def read_temp():
    valid, temp = read_temp_raw()

    while 'YES' not in valid:
        time.sleep(0.2)
        valid, temp = read_temp_raw()
    
    pos = temp.index('t=')
    if pos != -1:
        temp_string = temp[pos+2:]
        temp_c = float(temp_string)/1000.0 
        temp_f = temp_c * (9.0 / 5.0) + 32.0

        return temp_c, temp_f

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
        accualTime = t.time()
        global acTimePLusInterwal
        print('Aktualny czas:',accualTime)
        
        print('acTimePLusInterwal:',acTimePLusInterwal)
        print('accualTime - acTimePLusInterwal:',accualTime-acTimePLusInterwal)
        
        # if accualTime >acTimePLusInterwal +interval1:
        #     print('Interwal doliczyl do zadanej wartosci nastepuje triger')
        #     acTimePLusInterwal=accualTime
        #     print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', acTimePLusInterwal)
        # print("------------>>>>>>>>jestem w funkcji 'setOutputs' wyswietlam dane state:",state, 'Temp:', temp, 'Wydajnosc pompy:', pumpEfi)
        pick1=os.path.join(app.config["UPLOAD_FOLDER"], "6.jpg")
        if state and temp < 25.0:
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa woda urzytkowa - PonWU.jpg ")
            pick1=os.path.join(app.config["UPLOAD_FOLDER"], "PonWU.jpg")
        if state and temp > 25.0 and temp < 30.0:
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa centralne ogrzewanie PonCO.jpg ")
            pick1=os.path.join(app.config["UPLOAD_FOLDER"], "PonCO.jpg")
        if state==False:
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' ustawiam tlo na pompa wylaczona P_off.jpg ")
            pick1=os.path.join(app.config["UPLOAD_FOLDER"], "P_off.jpg")
            
        if state == True:
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek state == True", state)
            GPIO.output(pins[3], GPIO.HIGH)

        else:
           GPIO.output(pins[3], GPIO.LOW)
        
        if pumpEfi==0 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 0")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi==1 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 1")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 2 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 2")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 3 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 3")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 4 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 4")
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 5 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 5")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.HIGH)
        elif pumpEfi == 6 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 6")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.LOW)
        elif pumpEfi == 7 and state == True:
            BaseEfiInPercent = BaseEfiInPercent*pumpEfi
            print("------------>>>>>>>>jestem w funkcji 'setOutputs' sprawdzam warunek pumpEfi == 7")
            GPIO.output(pins[0], GPIO.HIGH)
            GPIO.output(pins[1], GPIO.HIGH)
            GPIO.output(pins[2], GPIO.HIGH)
        else:
            BaseEfiInPercent = 0
            GPIO.output(pins[0], GPIO.LOW)
            GPIO.output(pins[1], GPIO.LOW)
            GPIO.output(pins[2], GPIO.LOW)
           
        
        return pick1, round(BaseEfiInPercent,1)
def pumpControl():
    print('jestem w funkcji punpControl')

def checkPumpEfi(t_set: float, t_accual: float, offset: int):
        global pumpEfi
        interval1=6
        interval2=12
        accualTime = t.time()
        global acTimePLusInterwal
        print('JEstem w funkcji checkPumpEfi')
        print('Aktualny czas:',accualTime)
        print('acTimePLusInterwal:',acTimePLusInterwal)
        print('accualTime - acTimePLusInterwal:',accualTime-acTimePLusInterwal)
        print('drukuje typ zmiennej: t_set',type(t_set))
        print('drukuje typ zmiennej: t_accual',type(t_accual))
        print('drukuje typ zmiennej: offset',type(offset))
        print('drukuje typ zmiennej: pumpEfi',type(pumpEfi))
        if accualTime >acTimePLusInterwal + interval1:
            print('Interwal doliczyl do zadanej wartosci nastepuje triger')
            acTimePLusInterwal=accualTime
            
            if t_accual > (t_set + offset) and pumpEfi >= 0:
                print('Interwal doliczyl do zadanej wartosci nastepuje dekrementacja acTimePLusInterwal', acTimePLusInterwal)
                pumpEfi=pumpEfi-1
            elif t_accual < (t_set - offset) and pumpEfi < 7:
                print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', acTimePLusInterwal)
                pumpEfi=pumpEfi+1
        
        print("------------>>>>>>>>jestem w funkcji 'checkPumpEfi' wyswietlam dane t_set:",t_set, 't_accual:', t_accual, 'Wydajnosc pompy:', pumpEfi, 'offset:', offset)
if __name__ == "__main__":
        app.run(host='0.0.0.0', port = 5000, debug=True)
        
     

