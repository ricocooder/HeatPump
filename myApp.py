from flask import Flask, flash, render_template, request
from ReadTemp import read_temp
from flask_apscheduler import APScheduler
from setOutputs import setOutputs
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


app = Flask(__name__)
scheduler = APScheduler()


def scheduleTask():
    read_temp()
#     g.readTemp2 = read_temp(1)
#     g.readTemp3 = read_temp(2)
    # g.readTemp4 = read_temp(3)
    # g.readTemp5 = read_temp(4)
    checkPumpEfi(g.tz1, g.readTemp[0], 5)
    g.BaseEfiInPercent = setOutputs(g.mainState, g.readTemp[0], g.pumpEfi)
    print("This test runs every 3 seconds")


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
pickFolder = os.path.join("static")
app.config["UPLOAD_FOLDER"] = pickFolder

# g.c = read_temp()


@app.route('/')
def hello_world():
    output = request.form.to_dict()
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable')
                # print('error wrong variable')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_1 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_1 zostal wcisneity')
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.pumpEfi >= 0:
                g.pumpEfi = g.pumpEfi - 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_2 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_2 zostal wcisneity')
        if request.form.get('Turn OFF Pump') == 'Turn OFF Pump':
            g.mainState = False
            # print('-------->>>>>   przycisk wylaczenia pompy zostal wcisniety')
        if request.form.get('Turn ON Pump') == 'Turn ON Pump':
            # print('-------->>>>>   przycisk wlaczenia pompy zostal wcisniety')
            g.mainState = True
#     g.c = read_temp()
    pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "6.jpg")
    return render_template("index.html", t1=g.readTemp[0], to1=g.to1, t2=g.readTemp[1], to2=g.to2,t3=g.readTemp[2], to3=g.to3, t4=g.t4, to4=g.to4, t5=g.t5, to5=g.to5, t6=g.t6, to6=g.to6, tz1=g.tz1, tz2=g.tz2, tzo2=g.tzo2, image1=pick1, pump=g.BaseEfiInPercent, mainState=g.mainState)


@app.route("/result", methods=["POST", "GET"])
def result():
    output = request.form.to_dict()
    if request.form.get('Turn OFF Pump') == 'Turn OFF Pump':
        g.mainState = False
        flash('Pompa wyłączona', 'error')
        # print('-------->>>>>   przycisk wylaczenia pompy zostal wcisniety')
    if request.form.get('Turn ON Pump') == 'Turn ON Pump':
        flash('Pompa załączona', 'error')
        # print('-------->>>>>   przycisk wlaczenia pompy zostal wcisniety')
        g.mainState = True

#     g.c = read_temp()
#     g.BaseEfiInPercent = setOutputs(g.mainState, g.c, g.pumpEfi)
    pick1 = os.path.join(app.config["UPLOAD_FOLDER"], "6.jpg")

    return render_template("index.html", t1=g.readTemp[0], to1=g.to1, t2=g.readTemp[1], to2=g.to2, t3=g.readTemp[2], to3=g.to3, t4=g.t4, to4=g.to4, t5=g.t5, to5=g.to5, t6=g.t6, to6=g.to6, tz1=g.tz1, tz2=g.tz2, tzo2=g.tzo2, image1=pick1, pump=g.BaseEfiInPercent, mainState=g.mainState)


@app.route("/temp_sensor_config", methods=["POST", "GET"])
def temp_sensor_config():
    output = request.form.to_dict()
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable')
                # print('error wrong variable')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_1 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_1 zostal wcisneity')
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.pumpEfi >= 0:
                g.pumpEfi = g.pumpEfi - 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_2 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_2 zostal wcisneity')
    return render_template("temp_sensor_config.html", sensFoundNumber = g.tempSensFoundNumber, sensFoundList=g.readTemp)


@app.route("/settings", methods=["POST", "GET"])
def settings():
    output = request.form.to_dict()
    if request.method == 'POST':
        if request.form.get('Save1') == 'Save':
            try:
                g.tz1 = float(request.form['tempZad1'])
            except ValueError:
                flash('Error wrong input variable')
                # print('error wrong variable')
        if request.form.get('Save2') == 'Save':
            g.tz2 = request.form['tempZad2']
        if request.form.get('Przycisk_1') == 'Przycisk_1':
            if g.pumpEfi < 8:
                g.pumpEfi = g.pumpEfi + 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_1 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_1 zostal wcisneity')
        if request.form.get('Przycisk_2') == 'Przycisk_2':
            if g.pumpEfi >= 0:
                g.pumpEfi = g.pumpEfi - 1
            else:
                g.pumpEfi = 0
            # print('-------->>>>>   Przycisk_2 zostal wcisneity g.pumpEfi = ', g.pumpEfi)
            # print('-------->>>>>   Przycisk_2 zostal wcisneity')
    return render_template("settings.html", tz1=g.tz1, tz2=g.tz2,)


@app.route("/history", methods=["POST", "GET"])
def history():
    return render_template("history.html")


# def pumpControl():
    # print('jestem w funkcji punpControl')

def checkPumpEfi(t_set: float, t_accual: float, offset: int):
    interval1 = 60
    interval2 = 120
    accualTime = time.time()
    # print('JEstem w funkcji checkPumpEfi')
    # print('Aktualny czas:',accualTime)
    # print('acTimePLusInterwal:', g.acTimePLusInterwal)
    # print('accualTime - acTimePLusInterwal:',accualTime-g.acTimePLusInterwal)
    # print('drukuje typ zmiennej: t_set',type(t_set))
    # print('drukuje typ zmiennej: t_accual',type(t_accual))
    # print('drukuje typ zmiennej: offset',type(offset))
    # print('drukuje typ zmiennej: pumpEfi',type(g.pumpEfi))
    if accualTime > g.acTimePLusInterwal + interval1:
        # print('Interwal doliczyl do zadanej wartosci nastepuje triger')
        g.acTimePLusInterwal = accualTime

        if t_accual > (t_set + offset) and g.pumpEfi >= 0:
            # print('Interwal doliczyl do zadanej wartosci nastepuje dekrementacja acTimePLusInterwal', g.acTimePLusInterwal)
            g.pumpEfi = g.pumpEfi-1
        elif t_accual < (t_set - offset) and g.pumpEfi < 7:
            # print('Interwal doliczyl do zadanej wartosci nastepuje inkrementacja acTimePLusInterwal', g.acTimePLusInterwal)
            g.pumpEfi = g.pumpEfi+1

    # print("------------>>>>>>>>jestem w funkcji 'checkPumpEfi' wyswietlam dane t_set:",t_set, 't_accual:', t_accual, 'Wydajnosc pompy:', g.pumpEfi, 'offset:', offset)


if __name__ == "__main__":
    scheduler.add_job(id='Scheduled Task', func=scheduleTask,
                      trigger="interval", seconds=3)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
