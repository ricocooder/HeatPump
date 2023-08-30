from flask import Flask, flash, render_template, request
from ReadTemp import read_temp
from read_curr_woltage import read_CurrAndVolt
from flask_apscheduler import APScheduler
from setOutputs import setOutputs
from checkPumpEfi import checkPumpEfi
from mapValue import mapValue
import sqlite3
import datetime
import webbrowser
import time
import os
import globals as g
import saveToDB as db
import checkDispSpace as diskSpace

#TODO przygotowac kopie zapasowe kart
# DONE Podlaczyc modol wejsc analogowych
    # TODO podlaczyc czujnik natezenia i napiecia pradu
# DONE sprawdzic i potwierdzic poprawne sterowanie wszystkimi pinami
# TODO Dodac logike wyswietlania alarmu jak pojemosc karty jest bliska max przygotowane trzeba w "diskSpace.checkDiskSpace(10)"wpisac 80 i dodac do schedulera
# TODO Esport danych do pliku xlsx
# TODO Zapisywanie wszytkich nastaw na stale
# TODO pomiar zuzycia pradu/mocy moze warto tez dodac wykres mocy ? przygotowane - do sprawdzenia po podlaczenie czujnikow
# BUG 20.03.2023 23:16 ['/dev/root', '15G', '5,7G', '7,9G', '42%', '/']
# TODO posprzatac PumpEfi (wywolujemy funkcje z parametrami wejsciowymi a mozna to zrobic bez parametrow i zaczytywac z globalsow w sanej funkcji)
# DONE Dodac mechanizm sprawdzania ile jest przypisanych czjenikow przez utzytkowniaka a ile zostalo wyktytych w tablicy i obsluge bledu
    #TODO poprawic przypisywanie temperatury, od ktorej bedziemy regolowac (problem pojawia sie po wymianie czujnika lub po jego blednym przypisaniu)
# TODO Sprawdzic mozliwosc wygaszacza ekranu na pi oraz automatycznego odpalania tej strony full size
# TODO wyczyscic baze danych 
# DONE zmniejszyc czcionke w navbar
# DONE skasowac range picker z histori oraz poprawic wybieranie zakresu
# TODO dodac klawiature dotykowa na ekranie
# TODO dodac automatycznie otwierana przegladarke w trybie fullscreen
# DONE autostart aplikacji przy starcie systemu
# DONE dodac reczne sterowanie
    # DONE poprawic wizualizacje - dodac opis trybu pracy przez "popa pracuje/piec pracuje"
# DONE implementacja wykresow i danych historycznych
    # DONE bardziej czytelne wykresy, kolumny z danymi zawijane?
    # DONE poprawic style wyswietlania
# DONE uporzadkowac ekran ustawienia
# DONE harmonogram pracy pompy
# DONE dodac obrazek obok temepratur
# DONE dodac baze danych
# DONE dodac logike momenty zapisu do abzy dancyh
# DONE podlaczyc potencjoimetry w celu symulacji czujnika napiecia i pradu
# DONE rozwiazac problem kiedy mamy za duzo odczytanych czujnikow - sheduler wpada w blad i zawiszeja sie wejscia wyjscia - zwiekszyc interwal
# DONE Zrobic obsluge czujnokow w preli po sprawdzeniu ile jest czujnikow w tablicy
# DONE skasowalem to z histiry ale trzeba gdzies wrzucic  {% include 'ledStrip.html' %} tableka ze stanem przekaznikow - zrobione
# DONE stworzyc funkcjonalnosc do zapisywania fanych do db po wykryciu roznicy w wartosciach
# DONE dodat parametr sprawdzajacy ilosc wolnej przestrzeni na karcie SD

app = Flask(__name__)
scheduler = APScheduler()

def scheduleTask():
    read_temp()
    checkPumpEfi(g.setTemp[g.heatObject], g.readTemp[g.heatObject], g.pumpTempOfset, g.pumpInterval, g.heatObject)
    print("This test runs every 4 seconds")

def scheduleTask1s():
    g.BaseEfiInPercent = setOutputs(g.heatObject, g.readTemp[g.heatObject], g.pumpEfi)
    # read_CurrAndVolt()
    #FIXME włczyc po zakonczeniu testow
    g.pumpI = mapValue(g.pumpIread, 0, 1023, 0, 30)
    g.pumpV = mapValue(g.pumpVread, 0, 1023, 0, 250)
    g.pumpP = g.pumpI*g.pumpV/1000
    db.checkValues(1.0)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"] = pickFolder
pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "P_off_v3.jpg")

@app.route('/')
def hello_world():
    output = request.form.to_dict()
    global pick1
    return render_template("index.html", pumpI=g.pumpI, pumpV=g.pumpV, pumpP=round(g.pumpP, 2), image1=pick1, pump=g.BaseEfiInPercent, sensFoundList=g.readTemp,
                           discriptionList=g.discriptions, heatObject=g.heatObject, trybDiscriptions=g.trybDiscriptions, setTempList = g.setTemp, sezon=g.sezon, 
                           pins = g.pins, pinsDisc = g.pinsDisc, pinsLogic = g.pinsLogic, tempPins = g.tempPins)


@app.route("/result", methods=["POST", "GET"])
def result():
    output = request.form.to_dict()
    global pick1
    if request.form.get('Switch_mode'):
        if g.pumpMode == 'manual':
            flash('Włączony tryb Auto', 'primary')
            g.pumpMode = 'auto'
            g.heatObject = 2
        else:
            flash('Włączony tryb ręczny', 'primary')
            g.pumpMode = 'manual'
            g.heatObject = 0
            
 
             
              




    if request.form.get('0'):
        flash('Wcisniety przycisk odpowiadajcay za pin 0: Sterowanie pompy1 (NC)', 'success')
        if g.tempPins[0] == 1:
            g.tempPins[0] = 0
        else:
            g.tempPins[0] = 1
    if request.form.get('1'):
        flash('Wcisniety przycisk odpowiadajcay za pin 1: Sterowanie pompy2 (NC)','success')
        if g.tempPins[1] == 1:
            g.tempPins[1] = 0
        else:
            g.tempPins[1] = 1  
    if request.form.get('2'):
        flash('Wcisniety przycisk odpowiadajcay za pin 2: Sterowanie pompy3 (NC)', 'success')
        if g.tempPins[2] == 1:
            g.tempPins[2] = 0
        else:
            g.tempPins[2] = 1  
    if request.form.get('3'):
        flash('Wcisniety przycisk odpowiadajcay za pin 3: Zawor trojdrogowy (NO)', 'success')
        if g.tempPins[3] == 1:
            g.tempPins[3] = 0
        else:
            g.tempPins[3] = 1  
    if request.form.get('4'):
        flash('Wcisniety przycisk odpowiadajcay za pin 4: Sterownik piec (NC)', 'success')
        if g.tempPins[4] == 1:
            g.tempPins[4] = 0
        else:
            g.tempPins[4] = 1     
    if request.form.get('5'):
        flash('Wcisniety przycisk odpowiadajcay za pin 5: Zal/Wyl 24V (NC)', 'success')
        if g.tempPins[5] == 1:
            g.tempPins[5] = 0
        else:
            g.tempPins[5] = 1   
    if request.form.get('6'):
        flash('Wcisniety przycisk odpowiadajcay za pin 6: Pompa obiegowa (NC)', 'success')
        if g.tempPins[6] == 1:
            g.tempPins[6] = 0
        else:
            g.tempPins[6] = 1   
    if request.form.get('7'):
        flash('Wcisniety przycisk odpowiadajcay za pin 7: Spare', 'success')
        if g.tempPins[7] == 1:
            g.tempPins[7] = 0
        else:
            g.tempPins[7] = 1
    #     g.pumpMode = 'manual'
    #     g.heatObject = 0
    #     flash('Włączony tryb ręczny', 'primary')
    # if request.form.get('Turn ON Pump') == 'Turn ON Pump':
    #     flash('Włączony tryb automatyczny', 'success')
    #     g.pumpMode = 'auto'
    #     g.heatObject = 2
        
    #FIXME do skasowania po testach    
    if request.form.get('Switch'):
        flash('Zmiana Trybu Pracy', 'success')
        if g.heatObject ==2:
            g.heatObject = 0
        else:
            g.heatObject = g.heatObject+1

    if request.form.get('sezonSwitch'):
        flash('Zmiana Trybu Pracy', 'success')
        if g.sezon == 'Lato':
            g.sezon = 'Zima'
        else:
            g.sezon = 'Lato'
            
            
    if g.heatObject == 0:
        #pompa wylaczona - pracuje piec
        pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "P_off_v3.jpg")
    if g.heatObject == 2:
        #pompa pracuje - grzenia boilera
        pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "PonCO_v3.jpg")
    if g.heatObject == 1:
        #pompa pracuje - grzenia podlogi
        pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "PonWU_v3.jpg")
    return render_template("index.html", pumpI=g.pumpI, pumpV=g.pumpV, pumpP=round(g.pumpP, 2), image1=pick1, pump=g.BaseEfiInPercent, sensFoundList=g.readTemp,
                           discriptionList=g.discriptions, heatObject=g.heatObject, trybDiscriptions=g.trybDiscriptions, setTempList = g.setTemp, sezon=g.sezon, 
                           pins = g.pins, pinsDisc = g.pinsDisc, pinsLogic = g.pinsLogic, tempPins = g.tempPins, pumpMode = g.pumpMode)


@app.route("/temp_sensor_config", methods=["POST", "GET"])
def temp_sensor_config():
    output = request.form.to_dict()
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable', 'danger')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.pumpEfi >= 0:
                g.pumpEfi = g.pumpEfi - 1
            else:
                g.pumpEfi = 0
    return render_template("temp_sensor_config.html", sensFoundNumber = g.tempSensFoundNumber, sensFoundList=g.readTemp)

@app.route("/raspberrypi", methods=["POST", "GET"])
def raspberrypi():
            
    #FIXME zamiana odczytanej wartosci wolnego miejsca na int zeby gdzies to wyswietlic - zrobic z tego osobna funkcje i zapisywac gdzies
    if request.form.get('SaveDB'):
        flash('Odczyt z parametrow Raspberry Pi', 'success')
        diskSpace.checkDiskSpace(10)
        # g.diskSpaceList = diskSpace.getDf()
        # print(g.diskSpaceList)
        # print(g.diskSpaceList[4])
        # myvalue = g.diskSpaceList[4].replace('%','')
        # print(myvalue)
        # myvalue = int(myvalue)
        # print(type(myvalue))
        # print(myvalue)

    return render_template("raspberrypi.html", diskSpaceList = g.diskSpaceList, sensFoundList=g.readTemp)

@app.route("/settings", methods=["POST", "GET"])
def settings():
    global pick1
    output = request.form.to_dict()
    if request.method == 'POST':
        # obsluga przycisku zapisu temparatury podlogowki
        if request.form.get('Save1'):
            try:
                g.setTemp[2] = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable - dont use "," - use "." ', 'danger')
        # obsluga przycisku zapisu temparatury boilera
        if request.form.get('Save2'):
            try:
                g.setTemp[1] = float(request.form['tempZad2'])
            except ValueError:
                flash('Error wrong input variable - dont use "," - use "." ', 'danger')
        # obsluga przycisku zapisu interwal podlogowki
        if request.form.get('Save3'):
            try:
                g.pumpInterval[2] = int(request.form['setInterval1'])
            except ValueError:
                flash('Error wrong input variable', 'danger')
        # obsluga przycisku zapisu interwal boiler
        if request.form.get('Save4'):
            try:
                g.pumpInterval[1] = int(request.form['setInterval2'])
            except ValueError:
                flash('Error wrong input variable', 'danger')
        # obsluga przycisku zapisu offset podlogowka
        if request.form.get('Save5'):
            try:
                g.pumpTempOfset[2] = float(request.form['setAmplitude1'])
            except ValueError:
                flash('Error wrong input variable - dont use "," - use "." ', 'danger')
        # obsluga przycisku zapisu offset boiler
        if request.form.get('Save6'):
            try:
                g.pumpTempOfset[1] = float(request.form['setAmplitude2'])
            except ValueError:
                flash('Error wrong input variable - dont use "," - use "." ', 'danger')            
    return render_template("settings.html", setTempList=g.setTemp, pumpIntervalList=g.pumpInterval,
                            pumpTempOfsetList=g.pumpTempOfset, sensFoundList=g.readTemp )


                            
@app.route("/harmonogram", methods=["POST", "GET"])
def harmonogram():
    global pick1
    output = request.form.to_dict()
    if request.method == 'POST': 
        # obsluga przycisku zapisu harmonogramu godzina 0
        if request.form.get('0-1'):
            try:
                print(g.godzina[0][1])
                if g.godzina[0][1] == "ON":
                    g.godzina[0][1] = "OFF"
                else: g.godzina[0][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('0-2'):
            try:
                print(g.godzina[0][2])
                if g.godzina[0][2] == "ON":
                    g.godzina[0][2] = "OFF"
                else: g.godzina[0][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('0-3'):
            try:
                print(g.godzina[0][3])
                if g.godzina[0][3] == "ON":
                    g.godzina[0][3] = "OFF"
                else: g.godzina[0][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('0-4'):
            try:
                print(g.godzina[0][4])
                if g.godzina[0][4] == "ON":
                    g.godzina[0][4] = "OFF"
                else: g.godzina[0][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('0-5'):
            try:
                print(g.godzina[0][5])
                if g.godzina[0][5] == "ON":
                    g.godzina[0][5] = "OFF"
                else: g.godzina[0][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('0-6'):
            try:
                print(g.godzina[0][6])
                if g.godzina[0][6] == "ON":
                    g.godzina[0][6] = "OFF"
                else: g.godzina[0][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('0-7'):
            try:
                print(g.godzina[0][7])
                if g.godzina[0][7] == "ON":
                    g.godzina[0][7] = "OFF"
                else: g.godzina[0][7] = "ON"
            except ValueError:
                flash('Error cant asign value')    
        # obsluga przycisku zapisu harmonogramu godzina 1
        if request.form.get('1-1'):
            try:
                print(g.godzina[1][1])
                if g.godzina[1][1] == "ON":
                    g.godzina[1][1] = "OFF"
                else: g.godzina[1][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('1-2'):
            try:
                print(g.godzina[1][2])
                if g.godzina[1][2] == "ON":
                    g.godzina[1][2] = "OFF"
                else: g.godzina[1][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('1-3'):
            try:
                print(g.godzina[1][3])
                if g.godzina[1][3] == "ON":
                    g.godzina[1][3] = "OFF"
                else: g.godzina[1][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('1-4'):
            try:
                print(g.godzina[1][4])
                if g.godzina[1][4] == "ON":
                    g.godzina[1][4] = "OFF"
                else: g.godzina[1][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('1-5'):
            try:
                print(g.godzina[1][5])
                if g.godzina[1][5] == "ON":
                    g.godzina[1][5] = "OFF"
                else: g.godzina[1][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('1-6'):
            try:
                print(g.godzina[1][6])
                if g.godzina[1][6] == "ON":
                    g.godzina[1][6] = "OFF"
                else: g.godzina[1][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('1-7'):
            try:
                print(g.godzina[1][7])
                if g.godzina[1][7] == "ON":
                    g.godzina[1][7] = "OFF"
                else: g.godzina[1][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 2
        if request.form.get('2-1'):
            try:
                print(g.godzina[2][1])
                if g.godzina[2][1] == "ON":
                    g.godzina[2][1] = "OFF"
                else: g.godzina[2][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('2-2'):
            try:
                print(g.godzina[2][2])
                if g.godzina[2][2] == "ON":
                    g.godzina[2][2] = "OFF"
                else: g.godzina[2][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('2-3'):
            try:
                print(g.godzina[2][3])
                if g.godzina[2][3] == "ON":
                    g.godzina[2][3] = "OFF"
                else: g.godzina[2][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('2-4'):
            try:
                print(g.godzina[2][4])
                if g.godzina[2][4] == "ON":
                    g.godzina[2][4] = "OFF"
                else: g.godzina[2][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('2-5'):
            try:
                print(g.godzina[2][5])
                if g.godzina[2][5] == "ON":
                    g.godzina[2][5] = "OFF"
                else: g.godzina[2][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('2-6'):
            try:
                print(g.godzina[2][6])
                if g.godzina[2][6] == "ON":
                    g.godzina[2][6] = "OFF"
                else: g.godzina[2][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('2-7'):
            try:
                print(g.godzina[2][7])
                if g.godzina[2][7] == "ON":
                    g.godzina[2][7] = "OFF"
                else: g.godzina[2][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 3
        if request.form.get('3-1'):
            try:
                print(g.godzina[3][1])
                if g.godzina[3][1] == "ON":
                    g.godzina[3][1] = "OFF"
                else: g.godzina[3][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('3-2'):
            try:
                print(g.godzina[3][2])
                if g.godzina[3][2] == "ON":
                    g.godzina[3][2] = "OFF"
                else: g.godzina[3][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('3-3'):
            try:
                print(g.godzina[3][3])
                if g.godzina[3][3] == "ON":
                    g.godzina[3][3] = "OFF"
                else: g.godzina[3][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('3-4'):
            try:
                print(g.godzina[3][4])
                if g.godzina[3][4] == "ON":
                    g.godzina[3][4] = "OFF"
                else: g.godzina[3][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('3-5'):
            try:
                print(g.godzina[3][5])
                if g.godzina[3][5] == "ON":
                    g.godzina[3][5] = "OFF"
                else: g.godzina[3][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('3-6'):
            try:
                print(g.godzina[3][6])
                if g.godzina[3][6] == "ON":
                    g.godzina[3][6] = "OFF"
                else: g.godzina[3][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('3-7'):
            try:
                print(g.godzina[3][7])
                if g.godzina[3][7] == "ON":
                    g.godzina[3][7] = "OFF"
                else: g.godzina[3][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 4
        if request.form.get('4-1'):
            try:
                print(g.godzina[4][1])
                if g.godzina[4][1] == "ON":
                    g.godzina[4][1] = "OFF"
                else: g.godzina[4][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('4-2'):
            try:
                print(g.godzina[4][2])
                if g.godzina[4][2] == "ON":
                    g.godzina[4][2] = "OFF"
                else: g.godzina[4][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('4-3'):
            try:
                print(g.godzina[4][3])
                if g.godzina[4][3] == "ON":
                    g.godzina[4][3] = "OFF"
                else: g.godzina[4][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('4-4'):
            try:
                print(g.godzina[4][4])
                if g.godzina[4][4] == "ON":
                    g.godzina[4][4] = "OFF"
                else: g.godzina[4][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('4-5'):
            try:
                print(g.godzina[4][5])
                if g.godzina[4][5] == "ON":
                    g.godzina[4][5] = "OFF"
                else: g.godzina[4][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('4-6'):
            try:
                print(g.godzina[4][6])
                if g.godzina[4][6] == "ON":
                    g.godzina[4][6] = "OFF"
                else: g.godzina[4][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('4-7'):
            try:
                print(g.godzina[4][7])
                if g.godzina[4][7] == "ON":
                    g.godzina[4][7] = "OFF"
                else: g.godzina[4][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 5
        if request.form.get('5-1'):
            try:
                print(g.godzina[5][1])
                if g.godzina[5][1] == "ON":
                    g.godzina[5][1] = "OFF"
                else: g.godzina[5][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('5-2'):
            try:
                print(g.godzina[5][2])
                if g.godzina[5][2] == "ON":
                    g.godzina[5][2] = "OFF"
                else: g.godzina[5][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('5-3'):
            try:
                print(g.godzina[5][3])
                if g.godzina[5][3] == "ON":
                    g.godzina[5][3] = "OFF"
                else: g.godzina[5][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('5-4'):
            try:
                print(g.godzina[5][4])
                if g.godzina[5][4] == "ON":
                    g.godzina[5][4] = "OFF"
                else: g.godzina[5][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('5-5'):
            try:
                print(g.godzina[5][5])
                if g.godzina[5][5] == "ON":
                    g.godzina[5][5] = "OFF"
                else: g.godzina[5][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('5-6'):
            try:
                print(g.godzina[5][6])
                if g.godzina[5][6] == "ON":
                    g.godzina[5][6] = "OFF"
                else: g.godzina[5][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('5-7'):
            try:
                print(g.godzina[5][7])
                if g.godzina[5][7] == "ON":
                    g.godzina[5][7] = "OFF"
                else: g.godzina[5][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 6
        if request.form.get('6-1'):
            try:
                print(g.godzina[6][1])
                if g.godzina[6][1] == "ON":
                    g.godzina[6][1] = "OFF"
                else: g.godzina[6][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('6-2'):
            try:
                print(g.godzina[6][2])
                if g.godzina[6][2] == "ON":
                    g.godzina[6][2] = "OFF"
                else: g.godzina[6][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('6-3'):
            try:
                print(g.godzina[6][3])
                if g.godzina[6][3] == "ON":
                    g.godzina[6][3] = "OFF"
                else: g.godzina[6][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('6-4'):
            try:
                print(g.godzina[6][4])
                if g.godzina[6][4] == "ON":
                    g.godzina[6][4] = "OFF"
                else: g.godzina[6][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('6-5'):
            try:
                print(g.godzina[6][5])
                if g.godzina[6][5] == "ON":
                    g.godzina[6][5] = "OFF"
                else: g.godzina[6][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('6-6'):
            try:
                print(g.godzina[6][6])
                if g.godzina[6][6] == "ON":
                    g.godzina[6][6] = "OFF"
                else: g.godzina[6][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('6-7'):
            try:
                print(g.godzina[6][7])
                if g.godzina[6][7] == "ON":
                    g.godzina[6][7] = "OFF"
                else: g.godzina[6][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 7
        if request.form.get('7-1'):
            try:
                print(g.godzina[7][1])
                if g.godzina[7][1] == "ON":
                    g.godzina[7][1] = "OFF"
                else: g.godzina[7][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('7-2'):
            try:
                print(g.godzina[7][2])
                if g.godzina[7][2] == "ON":
                    g.godzina[7][2] = "OFF"
                else: g.godzina[7][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('7-3'):
            try:
                print(g.godzina[7][3])
                if g.godzina[7][3] == "ON":
                    g.godzina[7][3] = "OFF"
                else: g.godzina[7][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('7-4'):
            try:
                print(g.godzina[7][4])
                if g.godzina[7][4] == "ON":
                    g.godzina[7][4] = "OFF"
                else: g.godzina[7][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('7-5'):
            try:
                print(g.godzina[7][5])
                if g.godzina[7][5] == "ON":
                    g.godzina[7][5] = "OFF"
                else: g.godzina[7][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('7-6'):
            try:
                print(g.godzina[7][6])
                if g.godzina[7][6] == "ON":
                    g.godzina[7][6] = "OFF"
                else: g.godzina[7][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('7-7'):
            try:
                print(g.godzina[7][7])
                if g.godzina[7][7] == "ON":
                    g.godzina[7][7] = "OFF"
                else: g.godzina[7][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 8
        if request.form.get('8-1'):
            try:
                print(g.godzina[8][1])
                if g.godzina[8][1] == "ON":
                    g.godzina[8][1] = "OFF"
                else: g.godzina[8][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('8-2'):
            try:
                print(g.godzina[8][2])
                if g.godzina[8][2] == "ON":
                    g.godzina[8][2] = "OFF"
                else: g.godzina[8][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('8-3'):
            try:
                print(g.godzina[8][3])
                if g.godzina[8][3] == "ON":
                    g.godzina[8][3] = "OFF"
                else: g.godzina[8][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('8-4'):
            try:
                print(g.godzina[8][4])
                if g.godzina[8][4] == "ON":
                    g.godzina[8][4] = "OFF"
                else: g.godzina[8][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('8-5'):
            try:
                print(g.godzina[8][5])
                if g.godzina[8][5] == "ON":
                    g.godzina[8][5] = "OFF"
                else: g.godzina[8][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('8-6'):
            try:
                print(g.godzina[8][6])
                if g.godzina[8][6] == "ON":
                    g.godzina[8][6] = "OFF"
                else: g.godzina[8][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('8-7'):
            try:
                print(g.godzina[8][7])
                if g.godzina[8][7] == "ON":
                    g.godzina[8][7] = "OFF"
                else: g.godzina[8][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 9
        if request.form.get('9-1'):
            try:
                print(g.godzina[9][1])
                if g.godzina[9][1] == "ON":
                    g.godzina[9][1] = "OFF"
                else: g.godzina[9][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('9-2'):
            try:
                print(g.godzina[9][2])
                if g.godzina[9][2] == "ON":
                    g.godzina[9][2] = "OFF"
                else: g.godzina[9][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('9-3'):
            try:
                print(g.godzina[9][3])
                if g.godzina[9][3] == "ON":
                    g.godzina[9][3] = "OFF"
                else: g.godzina[9][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('9-4'):
            try:
                print(g.godzina[9][4])
                if g.godzina[9][4] == "ON":
                    g.godzina[9][4] = "OFF"
                else: g.godzina[9][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('9-5'):
            try:
                print(g.godzina[9][5])
                if g.godzina[9][5] == "ON":
                    g.godzina[9][5] = "OFF"
                else: g.godzina[9][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('9-6'):
            try:
                print(g.godzina[9][6])
                if g.godzina[9][6] == "ON":
                    g.godzina[9][6] = "OFF"
                else: g.godzina[9][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('9-7'):
            try:
                print(g.godzina[9][7])
                if g.godzina[9][7] == "ON":
                    g.godzina[9][7] = "OFF"
                else: g.godzina[9][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 10
        if request.form.get('10-1'):
            try:
                print(g.godzina[10][1])
                if g.godzina[10][1] == "ON":
                    g.godzina[10][1] = "OFF"
                else: g.godzina[10][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('10-2'):
            try:
                print(g.godzina[10][2])
                if g.godzina[10][2] == "ON":
                    g.godzina[10][2] = "OFF"
                else: g.godzina[10][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('10-3'):
            try:
                print(g.godzina[10][3])
                if g.godzina[10][3] == "ON":
                    g.godzina[10][3] = "OFF"
                else: g.godzina[10][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('10-4'):
            try:
                print(g.godzina[10][4])
                if g.godzina[10][4] == "ON":
                    g.godzina[10][4] = "OFF"
                else: g.godzina[10][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('10-5'):
            try:
                print(g.godzina[10][5])
                if g.godzina[10][5] == "ON":
                    g.godzina[10][5] = "OFF"
                else: g.godzina[10][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('10-6'):
            try:
                print(g.godzina[10][6])
                if g.godzina[10][6] == "ON":
                    g.godzina[10][6] = "OFF"
                else: g.godzina[10][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('10-7'):
            try:
                print(g.godzina[10][7])
                if g.godzina[10][7] == "ON":
                    g.godzina[10][7] = "OFF"
                else: g.godzina[10][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 11
        if request.form.get('11-1'):
            try:
                print(g.godzina[11][1])
                if g.godzina[11][1] == "ON":
                    g.godzina[11][1] = "OFF"
                else: g.godzina[11][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('11-2'):
            try:
                print(g.godzina[11][2])
                if g.godzina[11][2] == "ON":
                    g.godzina[11][2] = "OFF"
                else: g.godzina[11][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('11-3'):
            try:
                print(g.godzina[11][3])
                if g.godzina[11][3] == "ON":
                    g.godzina[11][3] = "OFF"
                else: g.godzina[11][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('11-4'):
            try:
                print(g.godzina[11][4])
                if g.godzina[11][4] == "ON":
                    g.godzina[11][4] = "OFF"
                else: g.godzina[11][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('11-5'):
            try:
                print(g.godzina[11][5])
                if g.godzina[11][5] == "ON":
                    g.godzina[11][5] = "OFF"
                else: g.godzina[11][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('11-6'):
            try:
                print(g.godzina[11][6])
                if g.godzina[11][6] == "ON":
                    g.godzina[11][6] = "OFF"
                else: g.godzina[11][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('11-7'):
            try:
                print(g.godzina[11][7])
                if g.godzina[11][7] == "ON":
                    g.godzina[11][7] = "OFF"
                else: g.godzina[11][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 12
        if request.form.get('12-1'):
            try:
                print(g.godzina[12][1])
                if g.godzina[12][1] == "ON":
                    g.godzina[12][1] = "OFF"
                else: g.godzina[12][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('12-2'):
            try:
                print(g.godzina[12][2])
                if g.godzina[12][2] == "ON":
                    g.godzina[12][2] = "OFF"
                else: g.godzina[12][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('12-3'):
            try:
                print(g.godzina[12][3])
                if g.godzina[12][3] == "ON":
                    g.godzina[12][3] = "OFF"
                else: g.godzina[12][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('12-4'):
            try:
                print(g.godzina[12][4])
                if g.godzina[12][4] == "ON":
                    g.godzina[12][4] = "OFF"
                else: g.godzina[12][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('12-5'):
            try:
                print(g.godzina[12][5])
                if g.godzina[12][5] == "ON":
                    g.godzina[12][5] = "OFF"
                else: g.godzina[12][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('12-6'):
            try:
                print(g.godzina[12][6])
                if g.godzina[12][6] == "ON":
                    g.godzina[12][6] = "OFF"
                else: g.godzina[12][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('12-7'):
            try:
                print(g.godzina[12][7])
                if g.godzina[12][7] == "ON":
                    g.godzina[12][7] = "OFF"
                else: g.godzina[12][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 13
        if request.form.get('13-1'):
            try:
                print(g.godzina[13][1])
                if g.godzina[13][1] == "ON":
                    g.godzina[13][1] = "OFF"
                else: g.godzina[13][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('13-2'):
            try:
                print(g.godzina[13][2])
                if g.godzina[13][2] == "ON":
                    g.godzina[13][2] = "OFF"
                else: g.godzina[13][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('13-3'):
            try:
                print(g.godzina[13][3])
                if g.godzina[13][3] == "ON":
                    g.godzina[13][3] = "OFF"
                else: g.godzina[13][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('13-4'):
            try:
                print(g.godzina[13][4])
                if g.godzina[13][4] == "ON":
                    g.godzina[13][4] = "OFF"
                else: g.godzina[13][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('13-5'):
            try:
                print(g.godzina[13][5])
                if g.godzina[13][5] == "ON":
                    g.godzina[13][5] = "OFF"
                else: g.godzina[13][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('13-6'):
            try:
                print(g.godzina[13][6])
                if g.godzina[13][6] == "ON":
                    g.godzina[13][6] = "OFF"
                else: g.godzina[13][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('13-7'):
            try:
                print(g.godzina[13][7])
                if g.godzina[13][7] == "ON":
                    g.godzina[13][7] = "OFF"
                else: g.godzina[13][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 14
        if request.form.get('14-1'):
            try:
                print(g.godzina[14][1])
                if g.godzina[14][1] == "ON":
                    g.godzina[14][1] = "OFF"
                else: g.godzina[14][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('14-2'):
            try:
                print(g.godzina[14][2])
                if g.godzina[14][2] == "ON":
                    g.godzina[14][2] = "OFF"
                else: g.godzina[14][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('14-3'):
            try:
                print(g.godzina[14][3])
                if g.godzina[14][3] == "ON":
                    g.godzina[14][3] = "OFF"
                else: g.godzina[14][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('14-4'):
            try:
                print(g.godzina[14][4])
                if g.godzina[14][4] == "ON":
                    g.godzina[14][4] = "OFF"
                else: g.godzina[14][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('14-5'):
            try:
                print(g.godzina[14][5])
                if g.godzina[14][5] == "ON":
                    g.godzina[14][5] = "OFF"
                else: g.godzina[14][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('14-6'):
            try:
                print(g.godzina[14][6])
                if g.godzina[14][6] == "ON":
                    g.godzina[14][6] = "OFF"
                else: g.godzina[14][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('14-7'):
            try:
                print(g.godzina[14][7])
                if g.godzina[14][7] == "ON":
                    g.godzina[14][7] = "OFF"
                else: g.godzina[14][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 15
        if request.form.get('15-1'):
            try:
                print(g.godzina[15][1])
                if g.godzina[15][1] == "ON":
                    g.godzina[15][1] = "OFF"
                else: g.godzina[15][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('15-2'):
            try:
                print(g.godzina[15][2])
                if g.godzina[15][2] == "ON":
                    g.godzina[15][2] = "OFF"
                else: g.godzina[15][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('15-3'):
            try:
                print(g.godzina[15][3])
                if g.godzina[15][3] == "ON":
                    g.godzina[15][3] = "OFF"
                else: g.godzina[15][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('15-4'):
            try:
                print(g.godzina[15][4])
                if g.godzina[15][4] == "ON":
                    g.godzina[15][4] = "OFF"
                else: g.godzina[15][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('15-5'):
            try:
                print(g.godzina[15][5])
                if g.godzina[15][5] == "ON":
                    g.godzina[15][5] = "OFF"
                else: g.godzina[15][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('15-6'):
            try:
                print(g.godzina[15][6])
                if g.godzina[15][6] == "ON":
                    g.godzina[15][6] = "OFF"
                else: g.godzina[15][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('15-7'):
            try:
                print(g.godzina[15][7])
                if g.godzina[15][7] == "ON":
                    g.godzina[15][7] = "OFF"
                else: g.godzina[15][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 16
        if request.form.get('16-1'):
            try:
                print(g.godzina[16][1])
                if g.godzina[16][1] == "ON":
                    g.godzina[16][1] = "OFF"
                else: g.godzina[16][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('16-2'):
            try:
                print(g.godzina[16][2])
                if g.godzina[16][2] == "ON":
                    g.godzina[16][2] = "OFF"
                else: g.godzina[16][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('16-3'):
            try:
                print(g.godzina[16][3])
                if g.godzina[16][3] == "ON":
                    g.godzina[16][3] = "OFF"
                else: g.godzina[16][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('16-4'):
            try:
                print(g.godzina[16][4])
                if g.godzina[16][4] == "ON":
                    g.godzina[16][4] = "OFF"
                else: g.godzina[16][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('16-5'):
            try:
                print(g.godzina[16][5])
                if g.godzina[16][5] == "ON":
                    g.godzina[16][5] = "OFF"
                else: g.godzina[16][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('16-6'):
            try:
                print(g.godzina[16][6])
                if g.godzina[16][6] == "ON":
                    g.godzina[16][6] = "OFF"
                else: g.godzina[16][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('16-7'):
            try:
                print(g.godzina[16][7])
                if g.godzina[16][7] == "ON":
                    g.godzina[16][7] = "OFF"
                else: g.godzina[16][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 17
        if request.form.get('17-1'):
            try:
                print(g.godzina[17][1])
                if g.godzina[17][1] == "ON":
                    g.godzina[17][1] = "OFF"
                else: g.godzina[17][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('17-2'):
            try:
                print(g.godzina[17][2])
                if g.godzina[17][2] == "ON":
                    g.godzina[17][2] = "OFF"
                else: g.godzina[17][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('17-3'):
            try:
                print(g.godzina[17][3])
                if g.godzina[17][3] == "ON":
                    g.godzina[17][3] = "OFF"
                else: g.godzina[17][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('17-4'):
            try:
                print(g.godzina[17][4])
                if g.godzina[17][4] == "ON":
                    g.godzina[17][4] = "OFF"
                else: g.godzina[17][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('17-5'):
            try:
                print(g.godzina[17][5])
                if g.godzina[17][5] == "ON":
                    g.godzina[17][5] = "OFF"
                else: g.godzina[17][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('17-6'):
            try:
                print(g.godzina[17][6])
                if g.godzina[17][6] == "ON":
                    g.godzina[17][6] = "OFF"
                else: g.godzina[17][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('17-7'):
            try:
                print(g.godzina[17][7])
                if g.godzina[17][7] == "ON":
                    g.godzina[17][7] = "OFF"
                else: g.godzina[17][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 18
        if request.form.get('18-1'):
            try:
                print(g.godzina[18][1])
                if g.godzina[18][1] == "ON":
                    g.godzina[18][1] = "OFF"
                else: g.godzina[18][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('18-2'):
            try:
                print(g.godzina[18][2])
                if g.godzina[18][2] == "ON":
                    g.godzina[18][2] = "OFF"
                else: g.godzina[18][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('18-3'):
            try:
                print(g.godzina[18][3])
                if g.godzina[18][3] == "ON":
                    g.godzina[18][3] = "OFF"
                else: g.godzina[18][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('18-4'):
            try:
                print(g.godzina[18][4])
                if g.godzina[18][4] == "ON":
                    g.godzina[18][4] = "OFF"
                else: g.godzina[18][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('18-5'):
            try:
                print(g.godzina[18][5])
                if g.godzina[18][5] == "ON":
                    g.godzina[18][5] = "OFF"
                else: g.godzina[18][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('18-6'):
            try:
                print(g.godzina[18][6])
                if g.godzina[18][6] == "ON":
                    g.godzina[18][6] = "OFF"
                else: g.godzina[18][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('18-7'):
            try:
                print(g.godzina[18][7])
                if g.godzina[18][7] == "ON":
                    g.godzina[18][7] = "OFF"
                else: g.godzina[18][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 19
        if request.form.get('19-1'):
            try:
                print(g.godzina[19][1])
                if g.godzina[19][1] == "ON":
                    g.godzina[19][1] = "OFF"
                else: g.godzina[19][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('19-2'):
            try:
                print(g.godzina[19][2])
                if g.godzina[19][2] == "ON":
                    g.godzina[19][2] = "OFF"
                else: g.godzina[19][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('19-3'):
            try:
                print(g.godzina[19][3])
                if g.godzina[19][3] == "ON":
                    g.godzina[19][3] = "OFF"
                else: g.godzina[19][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('19-4'):
            try:
                print(g.godzina[19][4])
                if g.godzina[19][4] == "ON":
                    g.godzina[19][4] = "OFF"
                else: g.godzina[19][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('19-5'):
            try:
                print(g.godzina[19][5])
                if g.godzina[19][5] == "ON":
                    g.godzina[19][5] = "OFF"
                else: g.godzina[19][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('19-6'):
            try:
                print(g.godzina[19][6])
                if g.godzina[19][6] == "ON":
                    g.godzina[19][6] = "OFF"
                else: g.godzina[19][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('19-7'):
            try:
                print(g.godzina[19][7])
                if g.godzina[19][7] == "ON":
                    g.godzina[19][7] = "OFF"
                else: g.godzina[19][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 20
        if request.form.get('20-1'):
            try:
                print(g.godzina[20][1])
                if g.godzina[20][1] == "ON":
                    g.godzina[20][1] = "OFF"
                else: g.godzina[20][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('20-2'):
            try:
                print(g.godzina[20][2])
                if g.godzina[20][2] == "ON":
                    g.godzina[20][2] = "OFF"
                else: g.godzina[20][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('20-3'):
            try:
                print(g.godzina[20][3])
                if g.godzina[20][3] == "ON":
                    g.godzina[20][3] = "OFF"
                else: g.godzina[20][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('20-4'):
            try:
                print(g.godzina[20][4])
                if g.godzina[20][4] == "ON":
                    g.godzina[20][4] = "OFF"
                else: g.godzina[20][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('20-5'):
            try:
                print(g.godzina[20][5])
                if g.godzina[20][5] == "ON":
                    g.godzina[20][5] = "OFF"
                else: g.godzina[20][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('20-6'):
            try:
                print(g.godzina[20][6])
                if g.godzina[20][6] == "ON":
                    g.godzina[20][6] = "OFF"
                else: g.godzina[20][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('20-7'):
            try:
                print(g.godzina[20][7])
                if g.godzina[20][7] == "ON":
                    g.godzina[20][7] = "OFF"
                else: g.godzina[20][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 21
        if request.form.get('21-1'):
            try:
                print(g.godzina[21][1])
                if g.godzina[21][1] == "ON":
                    g.godzina[21][1] = "OFF"
                else: g.godzina[21][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('21-2'):
            try:
                print(g.godzina[21][2])
                if g.godzina[21][2] == "ON":
                    g.godzina[21][2] = "OFF"
                else: g.godzina[21][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('21-3'):
            try:
                print(g.godzina[21][3])
                if g.godzina[21][3] == "ON":
                    g.godzina[21][3] = "OFF"
                else: g.godzina[21][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('21-4'):
            try:
                print(g.godzina[21][4])
                if g.godzina[21][4] == "ON":
                    g.godzina[21][4] = "OFF"
                else: g.godzina[21][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('21-5'):
            try:
                print(g.godzina[21][5])
                if g.godzina[21][5] == "ON":
                    g.godzina[21][5] = "OFF"
                else: g.godzina[21][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('21-6'):
            try:
                print(g.godzina[21][6])
                if g.godzina[21][6] == "ON":
                    g.godzina[21][6] = "OFF"
                else: g.godzina[21][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('21-7'):
            try:
                print(g.godzina[21][7])
                if g.godzina[21][7] == "ON":
                    g.godzina[21][7] = "OFF"
                else: g.godzina[21][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 22
        if request.form.get('22-1'):
            try:
                print(g.godzina[22][1])
                if g.godzina[22][1] == "ON":
                    g.godzina[22][1] = "OFF"
                else: g.godzina[22][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('22-2'):
            try:
                print(g.godzina[22][2])
                if g.godzina[22][2] == "ON":
                    g.godzina[22][2] = "OFF"
                else: g.godzina[22][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('22-3'):
            try:
                print(g.godzina[22][3])
                if g.godzina[22][3] == "ON":
                    g.godzina[22][3] = "OFF"
                else: g.godzina[22][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('22-4'):
            try:
                print(g.godzina[22][4])
                if g.godzina[22][4] == "ON":
                    g.godzina[22][4] = "OFF"
                else: g.godzina[22][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('22-5'):
            try:
                print(g.godzina[22][5])
                if g.godzina[22][5] == "ON":
                    g.godzina[22][5] = "OFF"
                else: g.godzina[22][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('22-6'):
            try:
                print(g.godzina[22][6])
                if g.godzina[22][6] == "ON":
                    g.godzina[22][6] = "OFF"
                else: g.godzina[22][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('22-7'):
            try:
                print(g.godzina[22][7])
                if g.godzina[22][7] == "ON":
                    g.godzina[22][7] = "OFF"
                else: g.godzina[22][7] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        # obsluga przycisku zapisu harmonogramu 23
        if request.form.get('23-1'):
            try:
                print(g.godzina[23][1])
                if g.godzina[23][1] == "ON":
                    g.godzina[23][1] = "OFF"
                else: g.godzina[23][1] = "ON"
            except ValueError:
                flash('Error cant asign value') 
        if request.form.get('23-2'):
            try:
                print(g.godzina[23][2])
                if g.godzina[23][2] == "ON":
                    g.godzina[23][2] = "OFF"
                else: g.godzina[23][2] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('23-3'):
            try:
                print(g.godzina[23][3])
                if g.godzina[23][3] == "ON":
                    g.godzina[23][3] = "OFF"
                else: g.godzina[23][3] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('23-4'):
            try:
                print(g.godzina[23][4])
                if g.godzina[23][4] == "ON":
                    g.godzina[23][4] = "OFF"
                else: g.godzina[23][4] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('23-5'):
            try:
                print(g.godzina[23][5])
                if g.godzina[23][5] == "ON":
                    g.godzina[23][5] = "OFF"
                else: g.godzina[23][5] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('23-6'):
            try:
                print(g.godzina[23][6])
                if g.godzina[23][6] == "ON":
                    g.godzina[23][6] = "OFF"
                else: g.godzina[23][6] = "ON"
            except ValueError:
                flash('Error cant asign value')
        if request.form.get('23-7'):
            try:
                print(g.godzina[23][7])
                if g.godzina[23][7] == "ON":
                    g.godzina[23][7] = "OFF"
                else: g.godzina[23][7] = "ON"
            except ValueError:
                flash('Error cant asign value')            
    return render_template("harmonogram.html", dni = g.dni, godzina = g.godzina, sensFoundList=g.readTemp)

def getDataFromDB(from_date_str, to_date_str):
    conn=sqlite3.connect('/home/pi/Documents/HeatPump/myDB.db')
    curs=conn.cursor()
    curs.execute("SELECT * FROM temp1 WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temp1 = curs.fetchall()
    print(temp1)
    curs.execute("SELECT * FROM temp2 WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temp2 = curs.fetchall()
    curs.execute("SELECT * FROM temp3 WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temp3 = curs.fetchall()
    curs.execute("SELECT * FROM volt WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    volt = curs.fetchall()
    curs.execute("SELECT * FROM cur WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    curr = curs.fetchall()
    curs.execute("SELECT * FROM efi WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    efi = curs.fetchall()
    conn.close()
    return temp1, temp2, temp3, volt, curr, efi

@app.route("/history", methods=["POST", "GET"])
def history():
    from_date_str   = request.args.get('from',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
    to_date_str     = request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
    
    range_h_int = 24

    # if request.form.get('SaveRange'):
    #     try:
    #         range_h_int = int(request.form['range_h'])
    #         # print(type(range_h_int), range_h_int)
    #     except:
    #         print("data tyme error")
    #         range_h_int = 48

    
    if not validate_date(from_date_str):      # Validate date before sending it to the DB
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")  # Validate date before sending it to the DB

    if from_date_str == to_date_str:
        time_now = datetime.datetime.now()
        time_from = time_now - datetime.timedelta(hours = range_h_int)
        time_to = time_now
        from_date_str = time_from.strftime(("%Y-%m-%d %H:%M"))
        to_date_str = time_to.strftime(("%Y-%m-%d %H:%M"))
    
    temp1, temp2, temp3, volt, curr, efi = getDataFromDB(from_date_str, to_date_str)
    return render_template("history.html", sensFoundList=g.readTemp, ledStrip = g.tempPins, ledStripDiscription=g.ledStripDiscription, temp1=temp1, temp2=temp2, temp3=temp3, 
                           volt=volt, curr=curr, efi=efi, temp_items1=len(temp1), temp_items2=len(temp2), temp_items3=len(temp3), volt_items=len(volt), curr_items=len(curr), 
                           efi_items=len(efi), from_date = from_date_str, to_date = to_date_str)


def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        flash('Zly format zakresu daty sprobuj tak: /history?from=2023-03-19 21:32&to=2023-03-19 22:00', 'danger')
        return False



if __name__ == "__main__":
    scheduler.add_job(id='Scheduled Task', func=scheduleTask,
                      trigger="interval", seconds=4)
    scheduler.add_job(id='Scheduler Task 1s', func=scheduleTask1s, 
                      trigger="interval", seconds=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
	