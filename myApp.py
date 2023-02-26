from flask import Flask, flash, render_template, request
from ReadTemp import read_temp
from setOutputs import setOutputs
import webbrowser
import time
import os
import globals as g

test = 0


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"]=pickFolder
mainState = True
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
                flash('Error wrong input variable')
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
                flash('Error wrong input variable')
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
    BaseEfiInPercent = setOutputs(mainState, c, pumpEfi)
    pick1=os.path.join(app.config["UPLOAD_FOLDER"], "6.jpg")
    checkPumpEfi(tz1, c, 5)
    return render_template("index.html", t1=c, to1=to1, t2=t2, to2=to2, t3=t3, to3=to3, t4=t4, to4=to4, t5=t5, to5=to5, t6=t6, to6=to6, tz1=tz1, tz2=tz2, tzo2=tzo2, image1=pick1, pump=BaseEfiInPercent, mainState=mainState)

@app.route("/settings", methods = ["POST", "GET"])
def settings():
    return render_template("settings.html")

@app.route("/history", methods = ["POST", "GET"])
def history():
    return render_template("history.html")




def pumpControl():
    print('jestem w funkcji punpControl')

def checkPumpEfi(t_set: float, t_accual: float, offset: int):
        global pumpEfi
        interval1=60
        interval2=120
        accualTime = time.time()
        print('JEstem w funkcji checkPumpEfi')
        print('Aktualny czas:',accualTime)
        print('acTimePLusInterwal:', g.acTimePLusInterwal)
        print('accualTime - acTimePLusInterwal:',accualTime-g.acTimePLusInterwal)
        print('drukuje typ zmiennej: t_set',type(t_set))
        print('drukuje typ zmiennej: t_accual',type(t_accual))
        print('drukuje typ zmiennej: offset',type(offset))
        print('drukuje typ zmiennej: pumpEfi',type(pumpEfi))
        if accualTime >g.acTimePLusInterwal + interval1:
            print('Interwal doliczyl do zadanej wartosci nastepuje triger')
            g.acTimePLusInterwal=accualTime
            
            if t_accual > (t_set + offset) and pumpEfi >= 0:
                print('Interwal doliczyl do zadanej wartosci nastepuje dekrementacja acTimePLusInterwal', g.acTimePLusInterwal)
                pumpEfi=pumpEfi-1
            elif t_accual < (t_set - offset) and pumpEfi < 7:
                print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', g.acTimePLusInterwal)
                pumpEfi=pumpEfi+1
        
        print("------------>>>>>>>>jestem w funkcji 'checkPumpEfi' wyswietlam dane t_set:",t_set, 't_accual:', t_accual, 'Wydajnosc pompy:', pumpEfi, 'offset:', offset)
if __name__ == "__main__":
        app.run(host='0.0.0.0', port = 5000, debug=True)
        
     

