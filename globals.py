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
t1=21
to1="zasilanie boiler"
t2=22
to2="zasilanie podlogowka"
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
