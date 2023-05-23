acTimePLusInterwal=0
pins = [26,5,6,12,25,24,23,16]
pinsDisc = ['Sterowanie pompy1 (NC)', 'Sterowanie pompy2 (NC)',
            'Sterowanie pompy3 (NC)', 'Zawor trojdrogowy (NO)',
            'sterownik piec (NC)', 'zal/wyl 24V (NC)', 'pompa obiegowa (NC)', 'Spare']
pinsLogic = ['NC', 'NC', 'NC', 'NO', 'NC', 'NC', 'NC', 'TBD']
tempPins = [0,0,0,0,0,0,0,0]
pumpEfi = 1
diskSpaceList=[]
heatObject=1 #0-nie dziala, 1-boiler, 2-podloga, 
pumpInterval = [0, 30, 60]
pumpTempOfset = [0, 2.0, 2.0]
sezon='Lato'
BaseEfiInPercent=0
BaseEfiInPercentTemp=0
tempSensFoundNumber=0
readTemp=[3.14]*64
readTempTemp=[3.14]*64
setTemp=[0, 50, 33]
pumpIread=0
pumpI=0
pumpItemp=0
pumpV=0
pumpVread=0
pumpVtemp=0
pumpP=0
trybDiscriptions=['Zew', 'Pompa - boiler', 'Pompa - podlogówka']
discriptions=['T1 - Zew', 'T2 - Bouler', 'T4 - Pompa powrot', 'T3 - Pompa wyjscie', 'T5 - Temp. zewnetrzna']
ledStripDiscription=['[1] Sterowanie bitowe wydajnosci pompy', '[2] Sterowanie bitowe wydajnosci pompy', '[3] Sterowanie bitowe wydajnosci pompy', 
                     '[4] Sterowanie bitowe wydajnosci pompy', '[5] Sterowanie bitowe wydajnosci pompy', '[6] Sterowanie bitowe wydajnosci pompy', 
                     '[7] Sterowanie bitowe wydajnosci pompy', '[8] Sterowanie bitowe wydajnosci pompy']
dni = ['Godzina\Dzien', 'Poniedzialek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
godzina = [
    ['0', 'ON', 'OFF', 'ON', 'ON', 'OFF', 'ON', 'ON'],
    ['1', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['2', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['3', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['4', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['5', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['6', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['7', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['8', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['9', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['10', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['11', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['12', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['13', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['14', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['15', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['16', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['17', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['18', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['19', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['20', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['21', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['22', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],
    ['23', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON', 'ON'],   
]