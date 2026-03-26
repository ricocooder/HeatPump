# Linux command df - report file system disk space usage
# Example:
# pi@raspberrypi ~ $ df -h /
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/root        30G  6.8G   22G  25% /
#
# This sample run "df -h /" in Python and get the result 
import os 
from flask import flash
import globals as g

def getDfDescription():
    df = os.popen("df -h /")
    i = 0
    while True:
        i = i + 1
        line = df.readline()
        if i==1:
            return(line.split()[0:6])
                                 
def getDf():
    df = os.popen("df -h /")
    i = 0
    while True:
        i = i + 1
        line = df.readline()
        if i==2:
            return(line.split()[0:6])

# Disk information
description = getDfDescription()
disk_root = getDf()

def checkDiskSpace(maxvalue):
    g.diskSpaceList = getDf()
    print('drukuje g.diskSpaceList', g.diskSpaceList)
    myvalue = g.diskSpaceList[4].replace('%','')
    print('drukuje myvalue z skasowanym procentem', myvalue)
    myvalue=int(myvalue)
    print('drukuje myvalue po zamiania na int', type(myvalue), myvalue)
    if myvalue >= maxvalue:
        flash('Karta pamieci zapelniona w ponad 80% ! Zrob cos z tym!', 'danger')