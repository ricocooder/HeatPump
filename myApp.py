from flask import Flask, flash, render_template, request
from ReadTemp import read_temp
from flask_apscheduler import APScheduler
from setOutputs import setOutputs
from checkPumpEfi import checkPumpEfi
from mapValue import mapValue
import webbrowser
import time
import os
import globals as g

# TODO uporzadkowac ekran ustawienia
# TODO dodac obrazek obok temepratur
# TODO dodac baze danych
# TODO dodac logike momenty zapisu do abzy dancyh
# TODO implementacje wykresow i danych histor
# TODO Podlaczyc modol wejsc analogowych
# TODO podlaczyc potencjoimetry w celu symulacji czujnika napiecia i pradu
# TODO rozwiazac problem kiedy mamy za duzo odczytanych czujnikow - sheduler wpada w blad i zawiszeja sie wejscia wyjscia
# TODO Dodac mechanizm sprawdzania ile jest przypisanych czjenikow przez utzytkowniaka a ile zostalo wyktytych w tablicy i obsluge bledu
# TODO Zrobic obsluge czujnokow w preli po sprawdzeniu ile jest czujnikow w tablicy
# TODO posprzatac PumpEfi (wywolujemy funkcje z parametrami wejsciowymi a mozna to zrobic bez parametrow i zaczytywac z globalsow w sanej funkcji)


app = Flask(__name__)
scheduler = APScheduler()

def scheduleTask():
    read_temp()
    checkPumpEfi(g.tz1, g.readTemp[2], g.pumpTempOfset, g.pumpInterval)
    print("This test runs every 4 seconds")

def scheduleTask1s():
    g.BaseEfiInPercent = setOutputs(g.mainState, g.readTemp[3], g.pumpEfi)
    g.pumpI = mapValue(443, 0, 1000, 0, 30)
    g.pumpV = mapValue(935, 0, 1000, 0, 250)
    g.pumpP = g.pumpI*g.pumpV/1000

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"] = pickFolder
pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "P_off_v3.jpg")

@app.route('/')
def hello_world():
    output = request.form.to_dict()
    global pick1
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable', 'danger')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.heatObject == 1:
                g.heatObject = 2
            else:
                g.heatObject = 1
        if request.form.get('Turn OFF Pump') == 'Turn OFF Pump':
            g.mainState = False
            g.heatObject = 0
        if request.form.get('Turn ON Pump') == 'Turn ON Pump':
            g.heatObject = 1
            g.mainState = True
    return render_template("index.html", t1=g.readTemp[0], t2=g.readTemp[1], t3=g.readTemp[2], 
                            t4=g.readTemp[3],  t5=g.readTemp[4], t6=g.readTemp[5], tz1=g.tz1, pumpI=g.pumpI, pumpV=g.pumpV, pumpP=round(g.pumpP, 2),
                            tzo2=g.tzo2, image1=pick1, pump=g.BaseEfiInPercent, mainState=g.mainState)


@app.route("/result", methods=["POST", "GET"])
def result():
    output = request.form.to_dict()
    global pick1
    if request.form.get('Turn OFF Pump') == 'Turn OFF Pump':
        g.heatObject = 0
        g.mainState = False
        flash('Pompa wyłączona', 'primary')
        pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "P_off_v3.jpg")
    if request.form.get('Turn ON Pump') == 'Turn ON Pump':
        flash('Pompa załączona', 'success')
        pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "PonCO_v3.jpg")
        g.heatObject = 2
        g.mainState = True

    return render_template("index.html", t1=g.readTemp[0], t2=g.readTemp[1],  t3=g.readTemp[2], 
                            t4=g.readTemp[3],  t5=g.readTemp[4], Tzadana=g.tz1, pumpI=g.pumpI, pumpV=g.pumpV, pumpP=round(g.pumpP, 2),
                            tzo2=g.tzo2, image1=pick1, pump=g.BaseEfiInPercent, mainState=g.mainState, sensFoundList=g.readTemp, discriptionList=g.discriptions,
                            heatObject=g.heatObject, trybDiscriptions=g.trybDiscriptions)


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
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.pumpEfi >= 0:
                g.pumpEfi = g.pumpEfi - 1
            else:
                g.pumpEfi = 0
    return render_template("temp_sensor_config.html", sensFoundNumber = g.tempSensFoundNumber, sensFoundList=g.readTemp)


@app.route("/settings", methods=["POST", "GET"])
def settings():
    global pick1
    output = request.form.to_dict()
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable', 'danger')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.heatObject == 1:
                g.heatObject = 2
                pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "PonCO_v3.jpg")
            else:
                g.heatObject = 1
                pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "PonWU_v3.jpg")
    return render_template("settings.html", setTempList=g.setTemp, pumpIntervalList=g.pumpInterval, 
                            pumpTempOfsetList=g.pumpTempOfset )


@app.route("/history", methods=["POST", "GET"])
def history():
    return render_template("history.html")

if __name__ == "__main__":
    scheduler.add_job(id='Scheduled Task', func=scheduleTask,
                      trigger="interval", seconds=4)
    scheduler.add_job(id='Scheduler Task 1s', func=scheduleTask1s, 
                      trigger="interval", seconds=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
