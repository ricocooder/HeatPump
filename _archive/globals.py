

language ={
    "home": ["Home", "Start"],
    "Settings": ["Settings","Nastawy"],
    "Schedule": ["Schedule", "Harmonogram"],
    "History/Charts": ["Charts", "Wykresy"],
    "Sensor configuration": ["Sensor config", "Konfig. czujnikow"],
    "RaspberryPi": ["Raspberry Pi", "Raspberry Pi"],
    "Temperature": ["Temperature", "Temperatura"],
    "Language": ["Language", "Język"],
    "Lang": ["en", "pl"],
    "LangChange": ["Change Language", "Zmiana Języka"],
    "OperatingMode": ["Operating mode", "Tryb pracy"],
    "SetTemp": ["set temp.", "temp. zadana"],
    "ActualVoltage": ["Actual Voltage", "Napięcie pompy"],
    "ActualCurrent": ["Actual Current", "Prąd pobierany"],
    "ActualPower": ["Actual Power", "Moc pompy"],
    "External": ["External", "Zewnętrzne"],
    "PumpBoiler": ["Pump - boiler", "Pompa - bojler"],
    "PumpFloorHeating": ["Pump - floor heating", "Pompa - ogrzewanie podłogowe"],
    "PumpOn": ["PumpOn", "Pompa pracuje"],
    "FiveOn": ["Five On", "Piec pracuje"],
    "RaspPiSett": ["Raspberry Pi settings", "Ustawienia Raspberry Pi"],
    "RaspPiDat": ["Memory card data", "Dane karty pamieci"],
    "RaspPiMem": ["Reading Pi memory", "Odczyt pamieci Pi"],
    "SensConfig": ["Sensor configuration", "Konfigoracja czujnikow"],
    "SensConfAssi": ["Here you can choose a name and assign a sensor number - this will be very important in the event of replacing the sensor.", 
                     "Tu mozesz wybrac nazwe, przypisac numer czujnika - bedzie to bardzo wazne w przypadku wymiany czujnika."],
    "SensConfDet": ["Number of sensors detected", "Wykryta liczba czujnikow"],
    "SensConfigDetNr": ["Sensor detected in array at index", "Sensor detected in array at index"],
    "SensConfIndic": ["actual value", "wartosc aktualna"],
    "SensConfOrder": ["Location of sensors on the list, after replacing the sensor, keep this order: [outside, boiler, pumpOut, pumpIn]", 
                      "Umiejscowienie czujnikow na liscie, po wymianie czujnika trzeba zachowac ta kolejnosc: [outside, boiler, pumpOut, pumpIn]"],
    "SensConfigCurr": ["Currently", "Obecnie"],
    "SensConfig1": ["Should the temperature be regulated in the boiler heating mode in relation to the sensor?", "Regulacja temperatury w trybie grzania bojlera ma odbyc sie wzgledem czujnika? "],
    "SensConfig2": ["Should the temperature be adjusted in the underfloor heating mode with respect to the sensor?", "Regulacja temperatury w trybie grzania podłogówki ma odbyc sie wzgledem czujnika?"],
    "SensConfig3": ["Outside temperature reading?", "Odczyt temparatury zewnetrznej?"],
    "SensConfig4": ["Odczyt temparatury zewnetrznej?", "Odczyt temparatury na wejsciu do pompy (niska temp)?"],
    "SensConfig5": ["Temperature reading at the pump outlet (high temperature)?", "Odczyt temparatury na wyjsciu z pompy (wysoka temp)?"],
    "DataDBDegrees": ["Degrees [C\xb0]", "Stopnie [C\xb0]"],
    "DataDBTempOut": ["Outdoor temperature", "Temperatura zewnętrzna"],
    "DataDBBoilTemp": ["Boiler temperature", "Temperatura bojlera"],
    "DataDBBPumpTemp": ["Pump output temperature", "Temperatura wyjscie pompy"],
    "DataDBBPumpAmp": ["Amperes [A]", "Ampery [A]"],
    "DataDBBPumpCurr": ["Current", "Prąd"],
    "DataDBBPumpVolt": ["Volt [V]", "Volt [V]"],
    "DataDBBPumpVoltage": ["Voltage", "Napięcie"],


}

acTimePLusInterwal=0
pins = [26,5,6,12,25,24,23,16]
pinsDisc = ['Sterowanie pompy1 (NC)', 'Sterowanie pompy2 (NC)',
            'Sterowanie pompy3 (NC)', 'Zawor trojdrogowy (NO)',
            'Sterownik piec (NC)', 'Zal/Wyl 24V (NC)', 'Pompa obiegowa (NC)', 'Spare']
pinsLogic = ['NC', 'NC', 'NC', 'NO', 'NC', 'NC', 'NC', 'TBD']
tempPins = [0,0,0,0,0,0,0,0]
pumpEfi = 1
pickedLang = 1 # 1 = pl; 0 = en
diskSpaceList=[]
heatObject=1 #0-nie dziala, 1-boiler, 2-podloga, 
pumpInterval = [0, 30, 60]
pumpTempOfset = [0, 2.0, 2.0]
pumpMode = 'auto'
sezon='Lato'
BaseEfiInPercent=0
BaseEfiInPercentTemp=0
tempSensFoundNumber=0
readTemp=[3.14]*6
readTempTemp=[2.14]*6
sensorIndexList=[0,1,3,2] #[outside, boiler, pumpOut, pumpIn]
setTemp=[0, 45, 33]
pumpIread=0
pumpI=9.7
pumpItemp=0
pumpV=232
pumpVread=0
pumpVtemp=0
pumpP=30
discriptions=['T1 - Zew', 'T2 - Bojler', 'T3 - Pompa wyjscie', 'T4 - Pompa powrot', 'T5 - Temp. zewnetrzna']
ledStripDiscription=['[1] Sterowanie bitowe wydajnosci pompy', '[2] Sterowanie bitowe wydajnosci pompy', '[3] Sterowanie bitowe wydajnosci pompy', 
                     '[4] Sterowanie bitowe wydajnosci pompy', '[5] Sterowanie bitowe wydajnosci pompy', '[6] Sterowanie bitowe wydajnosci pompy', 
                     '[7] Sterowanie bitowe wydajnosci pompy', '[8] Sterowanie bitowe wydajnosci pompy']
dni = {
        "1":["Time\Day", "Godzina\Dzień"],
        "2":["Monday", "Poniedziałek"],
        "3":["Tuesday", "Wtorek"],
        "4":["Wednesday", "Środa"],
        "5":["Thursday", "Czwartek"],
        "6":["Friday", "Piątek"],
        "7":["Saturday", "Sobota"],
        "8":["Sunday", "Niedziela"]}
godzina = [
    ['0', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['1', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['2', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['3', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['4', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['5', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['6', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['7', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['8', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['9', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['10', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['11', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['12', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['13', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['14', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['15', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['16', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['17', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'ON', 'ON'],
    ['18', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['19', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['20', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['21', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['22', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],
    ['23', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF', 'OFF'],   
]
