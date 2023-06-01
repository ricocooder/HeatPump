<h1>Jak ustawic stale IP</h1>
http://bbmagic.net/to-proste-jak-ustawic-statyczne-ip-w-raspberry-pi/

trzeba zainstalowac biblioteki adafruit do obslugi rozszerzenie wejsc analogowych


To add support for OneWire, we first need to open up the boot config file, and this can be done by running the following command. to do that I have used a nano text editor, you can use Terminal for that by entering the below command

sudo nano /boot/config.txt
Next At the bottom of this file enter the following.

dtoverlay=w1-gpio
Once done save and exit by pressing CTRL + X any enter Yes(Y).. Now reboot the Pi by running the following command.

sudo reboot
Once the Raspberry Pi has booted back up, we need to run modprobe so we can load the correct modules.

sudo modprobe w1-gpio
Then

sudo modprobe w1-therm
Now change into the devices directory and use the ls command to see the folders and files in the directory.

cd /sys/bus/w1/devices 
ls
List the file and a 28-xxxxxxxxxxxx device directory (e.g. here is 28-00000674869d) will be found. This is the ROM of DS18B20. If more than one DS18B20 is connected, you will find a certain directory of more than one.

![RasGPIO](https://user-images.githubusercontent.com/49715875/222986709-da9dd3c8-94d3-4a31-a984-e5ee746206e3.png)



czyszczenie bazy danych :
sqlite3 myDB.db
SQLite version 3.27.2 2019-02-25 16:06:06
Enter ".help" for usage hints.
sqlite> .tables
cur    efi    temp1  temp2  temp3  temp4  temp5  volt 
sqlite> DELETE FROM temp1;
sqlite> DELETE FROM temp2;
sqlite> DELETE FROM temp3;
sqlite> DELETE FROM temp4;
sqlite> DELETE FROM temp5;
sqlite> 