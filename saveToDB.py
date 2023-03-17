import sqlite3
import sys

def log_values(temp1, temp2,temp3, curr, volt, efi):
	conn=sqlite3.connect('/home/pi/Documents/HeatPump/myDB.db')  #It is important to provide an
							     #absolute path to the database
							     #file, otherwise Cron won't be
							     #able to find it!
	# For the time-related code (record timestamps and time-date calculations) to work 
	# correctly, it is important to ensure that your Raspberry Pi is set to UTC.
	# This is done by default!
	# In general, servers are assumed to be in UTC.
	curs=conn.cursor()
	curs.execute("""INSERT INTO temp1 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",temp1))
	curs.execute("""INSERT INTO temp2 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",temp2))
	curs.execute("""INSERT INTO temp3 values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",temp3))
	curs.execute("""INSERT INTO volt values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",volt))
	curs.execute("""INSERT INTO cur values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",curr))
	curs.execute("""INSERT INTO efi values(datetime(CURRENT_TIMESTAMP, 'localtime'),
         (?), (?))""", ("1",efi))
	
	conn.commit()
	conn.close()

# If you don't have a sensor but still wish to run this program, comment out all the 
# sensor related lines, and uncomment the following lines (these will produce random
# numbers for the temperature and humidity variables):
# import random
# humidity = random.randint(1,100)
# temperature = random.randint(10,30)
# if humidity is not None and temperature is not None:
# 	log_values("1", temperature, humidity)	
# else:
# 	log_values("1", -999, -999)