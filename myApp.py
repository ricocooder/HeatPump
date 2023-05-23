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


# TODO Dodac logike wyswietlania alarmu jak pojemosc karty jest bliska max 
# TODO Esport danych do pliku xlsx
# TODO Zapisywanie wszytkich nastaw na stale
# TODO pomiar zuzycia pradu/mocy moze warto tez dodac wykres mocy ?
# TODO dodac reczne sterowanie
# BUG 20.03.2023 23:16 ['/dev/root', '15G', '5,7G', '7,9G', '42%', '/']
# DONE implementacja wykresow i danych historycznych
    # TODO bardziej czytelne wykresy, kolumny z danymi zawijane?
    # TODO poprawic style wyswietlania
# TODO Podlaczyc modol wejsc analogowych
# TODO posprzatac PumpEfi (wywolujemy funkcje z parametrami wejsciowymi a mozna to zrobic bez parametrow i zaczytywac z globalsow w sanej funkcji)
# DONE Dodac mechanizm sprawdzania ile jest przypisanych czjenikow przez utzytkowniaka a ile zostalo wyktytych w tablicy i obsluge bledu
    #TODO poprawic przypisywanie temperatury, od ktorej bedziemy regolowac (problem pojawia sie po wymianie czujnika lub po jego blednym przypisaniu)
# DONE uporzadkowac ekran ustawienia
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
    #read_CurrAndVolt()
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
    if request.form.get('Turn OFF Pump') == 'Turn OFF Pump':
        g.heatObject = 0
        flash('Pompa wyłączona', 'primary')
    if request.form.get('Turn ON Pump') == 'Turn ON Pump':
        flash('Pompa załączona', 'success')
        g.heatObject = 2
        
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
                           pins = g.pins, pinsDisc = g.pinsDisc, pinsLogic = g.pinsLogic, tempPins = g.tempPins)


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
        # obsluga przycisku zapisu harmonogramu
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
    return render_template("settings.html", setTempList=g.setTemp, pumpIntervalList=g.pumpInterval, dni = g.dni, godzina = g.godzina,
                            pumpTempOfsetList=g.pumpTempOfset, sensFoundList=g.readTemp )
def getDataFromDB(from_date_str, to_date_str):
    conn=sqlite3.connect('/home/pi/Documents/HeatPump/myDB.db')
    curs=conn.cursor()
    curs.execute("SELECT * FROM temp1 WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
    temp1 = curs.fetchall()
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
    
    range_h_int = "nan"

    if request.form.get('SaveRange'):
        try:
            range_h_int = int(request.form['range_h'])
            # print(type(range_h_int), range_h_int)
        except:
            print("data tyme error")
            range_h_int = 48

    
    if not validate_date(from_date_str):      # Validate date before sending it to the DB
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")  # Validate date before sending it to the DB

    if isinstance(range_h_int, int):
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
	