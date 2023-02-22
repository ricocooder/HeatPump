# import sys
# from PyQt5.QtCore import pyqtSlot
# from PyQt5.QtWidgets import QApplication, QDialog
# from PyQt5.uic import loadUi
# import RPi.GPIO as gpio

import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication,QDialog
from PyQt5.uic import loadUi
import RPi.GPIO as gpio

input1 = 26

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

gpio.setup(input1, gpio.OUT)

class industrial(QDialog):
    def __init__(self):
        super(industrial,self).__init__()
        loadUi('wizka.ui', self)
        self.pbStart.clicked.connect(self.bp_Start)
        
        @pyqtSlot()
        def bp_Start(self):
            if gpio.input(input1):
                gpio.uotput(input1,gpio.LOW)
                self.pb_Start.setText('runing')
            else:
                gpio.output(input1,gpio.HIGH)
                self.pb_Start.setText('stoped')
                
                
                
app=QApplication(sys.argv)
widget=industrial()
widget.show()
sys.exit(app.exec_())