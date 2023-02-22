import RPi.GPIO as GPIO
import time as t

# TODO:
#     sprawdzic jak sterowac pompa (mamy 3 piny oraz sterujemy skokowo wydajnoscia pompy, poszykac w necie zaleznosci)


SleepTime = 2

GPIO.setmode(GPIO.BCM)
pins = [26,5,6,12,25,24,23,22]
pumpModeLvl = 1

try:
    while True:
        if pumpModeLvl == 1:
            
            GPIO.setup(pins[0], GPIO.OUT)
            GPIO.output(pins[0], GPIO.HIGH)
            t.sleep(SleepTime);
            GPIO.output(pins[0], GPIO.LOW)
            t.sleep(SleepTime);
#         for i in pins:
#             GPIO.setup(i, GPIO.OUT)
#             print('jestem w petli, zaraz odpalam gpio ',i,'-high')
#             GPIO.output(i, GPIO.HIGH)
#             print('gpio odpalone zaraz czekam dalay')
#             t.sleep(SleepTime);
#             print('odczekalem delay wylaczam gpio ',i,' - low')
#             GPIO.output(i, GPIO.LOW)
#             print('gpio ',i,' wylaczone - low')
#             t.sleep(SleepTime)
#         
        
except KeyboardInterrupt:
    print('Quit')
    
    GPIO.cleanup()
    