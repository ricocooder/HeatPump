from flask import Flask, flash, render_template, request
from ReadTemp import read_temp
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

# DONE uporzadkowac ekran ustawienia
# DONE dodac obrazek obok temepratur
# DONE dodac baze danych
# DONE dodac logike momenty zapisu do abzy dancyh
# BUG 20.03.2023 23:16 ['/dev/root', '15G', '5,7G', '7,9G', '42%', '/']
# TODO implementacja wykresow i danych historycznych
# TODO Podlaczyc modol wejsc analogowych
# TODO podlaczyc potencjoimetry w celu symulacji czujnika napiecia i pradu
# TODO rozwiazac problem kiedy mamy za duzo odczytanych czujnikow - sheduler wpada w blad i zawiszeja sie wejscia wyjscia
# TODO Dodac mechanizm sprawdzania ile jest przypisanych czjenikow przez utzytkowniaka a ile zostalo wyktytych w tablicy i obsluge bledu
# DONE Zrobic obsluge czujnokow w preli po sprawdzeniu ile jest czujnikow w tablicy
# TODO posprzatac PumpEfi (wywolujemy funkcje z parametrami wejsciowymi a mozna to zrobic bez parametrow i zaczytywac z globalsow w sanej funkcji)
# TODO skasowalem to z histiry ale trzeba gdzies wrzucic  {% include 'ledStrip.html' %}
# DONE stworzyc funkcjonalnosc do zapisywania fanych do db po wykryciu roznicy w wartosciach
# TODO dodat parametr sprawdzajacy ilosc wolnej przestrzeni na karcie SD
# TODO Esport danych do pliku xlsx
# TODO Zapisywanie wszytkich nastaw na stale

app = Flask(__name__)
scheduler = APScheduler()

def scheduleTask():
    read_temp()
    checkPumpEfi(g.setTemp[g.heatObject], g.readTemp[g.heatObject], g.pumpTempOfset, g.pumpInterval, g.heatObject)
    print("This test runs every 4 seconds")

def scheduleTask1s():
    # g.BaseEfiInPercent = setOutputs(g.heatObject, g.readTemp[g.heatObject], g.pumpEfi)
    db.checkValues(1)
    #FIXME włczyc po zakonczeniu testow
    # g.pumpI = mapValue(443, 0, 1000, 0, 30)
    # g.pumpV = mapValue(935, 0, 1000, 0, 250)
    g.pumpP = g.pumpI*g.pumpV/1000

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"] = pickFolder
pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "P_off_v3.jpg")

@app.route('/')
def hello_world():
    output = request.form.to_dict()
    global pick1
    return render_template("index.html", tz1=g.tz1, pumpI=g.pumpI, pumpV=g.pumpV, pumpP=round(g.pumpP, 2),
                            tzo2=g.tzo2, image1=pick1, pump=g.BaseEfiInPercent)


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
        
    #FIXME zamiana odczytanej wartosci wolnego miejsca na int zeby gdzies to wyswietlic - zrobic z tego osobna funkcje i zapisywac gdzies
    if request.form.get('SaveDB'):
        flash('Zmiana Trybu Pracy', 'success')
        diskSpace.checkDiskSpace(10)
        # g.diskSpaceList = diskSpace.getDf()
        # print(g.diskSpaceList)
        # print(g.diskSpaceList[4])
        # myvalue = g.diskSpaceList[4].replace('%','')
        # print(myvalue)
        # myvalue = int(myvalue)
        # print(type(myvalue))
        # print(myvalue)
        
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
                           discriptionList=g.discriptions, heatObject=g.heatObject, trybDiscriptions=g.trybDiscriptions, setTempList = g.setTemp, sezon=g.sezon)


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
    
    
    if not validate_date(from_date_str):      # Validate date before sending it to the DB
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")  # Validate date before sending it to the DB

    
    temp1, temp2, temp3, volt, curr, efi = getDataFromDB(from_date_str, to_date_str)
    return render_template("history.html", sensFoundList=g.readTemp, ledStrip = g.tempPins, ledStripDiscription=g.ledStripDiscription,
                           temp1=temp1, temp2=temp2, temp3=temp3, volt=volt, curr=curr, efi=efi, temp_items1=len(temp1), temp_items2=len(temp2), temp_items3=len(temp3), volt_items=len(volt), curr_items=len(curr), efi_items=len(efi))


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
	