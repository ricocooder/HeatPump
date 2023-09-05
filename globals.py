

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
    "ActualCurrent": ["Actual Current", "Prąd ponbierany"],
    "ActualPower": ["Actual Power", "Moc pompy"],
    "External": ["External", "Zewnętrzne"],
    "PumpBoiler": ["Pump - boiler", "Pompa - bojler"],
    "PumpFloorHeating": ["Pump - floor heating", "Pompa - ogrzewanie podłogowe"],
    "PumpOn": ["PumpOn", "Pompa pracuje"],
    "FiveOn": ["Five On", "Piec pracuje"],


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
setTemp=[0, 50, 33]
pumpIread=0
pumpI=9.7
pumpItemp=0
pumpV=232
pumpVread=0
pumpVtemp=0
pumpP=30
discriptions=['T1 - Zew', 'T2 - Bouler', 'T3 - Pompa wyjscie', 'T4 - Pompa powrot', 'T5 - Temp. zewnetrzna']
ledStripDiscription=['[1] Sterowanie bitowe wydajnosci pompy', '[2] Sterowanie bitowe wydajnosci pompy', '[3] Sterowanie bitowe wydajnosci pompy', 
                     '[4] Sterowanie bitowe wydajnosci pompy', '[5] Sterowanie bitowe wydajnosci pompy', '[6] Sterowanie bitowe wydajnosci pompy', 
                     '[7] Sterowanie bitowe wydajnosci pompy', '[8] Sterowanie bitowe wydajnosci pompy']
dni = ['Godzina\Dzień', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
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
