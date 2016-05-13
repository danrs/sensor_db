#!/usr/bin/python

# Import sensor/actuator libraries
import Adafruit_BMP.BMP085 as BMP085 #BMP085/BMP180 temperature and humdity sensor
import gps
import python_i2c_heart_rate_sensor as heartsense
import python_i2c_mpu9250 as mpu #10dof imu
import python_mq5_gas_sensor as mq5 #gas sensor
import python_vibration_motor as v_m

# Import other stuff we need
import argparse
import MySQLdb as mdb
import sys
import time

# Database settings (change these here if you need to)
dbhost = 'localhost'
dbuser = 'cat'
dbpword = 'cat'
dbname = 'catdb'


def dbinit(cursor):
    """
    Set up the necessary tables for each sensor in the database
    """
    cursor.execute('SET sql_notes = 0;') # disable warnings in case tables already exist
    cursor.execute('CREATE TABLE IF NOT EXISTS heartrate (time TIMESTAMP, bpm INTEGER);')
    cursor.execute("""CREATE TABLE IF NOT EXISTS imu (time TIMESTAMP, temp INTEGER,
                      ax INTEGER, ay INTEGER, az INTEGER,
                      wx INTEGER, wy INTEGER, wz INTEGER,
                      mx INTEGER, my INTEGER, mz INTEGER);""")
    cursor.execute('CREATE TABLE IF NOT EXISTS gas (time TIMESTAMP, raw_value INTEGER);')
    cursor.execute("""CREATE TABLE IF NOT EXISTS gps (time TIMESTAMP, gps_time TIMESTAMP,
                      satellites INTEGER, latitude VARCHAR(9), longitude VARCHAR(9));""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS environment (time TIMESTAMP,
                      temperature DOUBLE, pressure DOUBLE, altitude DOUBLE);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS motors (time TIMESTAMP, m1_status INTEGER,
                    m2_status INTEGER);""")
    cursor.execute('SET sql_notes = 1;') # re-enable warnings


if __name__ == '__main__':
    print 'Connecting to database'
    try:
        # set up database connection
        con = mdb.connect(dbhost, dbuser, dbpword, dbname);
        cur = con.cursor()
        dbinit(cur)

        # set up sensors
        ignore = {}
        motor1 = v_m.vibration_motor("P9_17")   # connect to I2C1 connector
        motor2 = v_m.vibration_motor("P9_26")   # connect to UART1 connector
        gas_sensor = mq5.mq5()                  # AIN0 is default pin
        try:
            heart_sensor = heartsense.heartsense()  # I2C2 bus
            ignore['heartrate'] = False
        except IOError as e:
            print 'Heart rate sensor not connected, ignoring sensor'
            ignore['heartrate'] = True
        try:
            imu_sensor = mpu.mpu9250()              # I2C2 bus
            ignore['imu_sensor'] = False
        except IOError as e:
            print 'IMU not connected, ignoring sensor'
            ignore['imu_sensor'] = True
        try:
            bmp_sensor = BMP085.BMP085()            # I2C2 bus
            ignore['bmp_sensor'] = False
        except IOError as e:
            print 'Barometer and temperature sensor not connected, ignoring sensor'
            ignore['bmp_sensor'] = True
        gps_sensor = gps.gps("localhost", "2947") # UART1 bus


    except mdb.Error as e:
        print 'Database Error %d: %s' % (e.args[0],e.args[1])
        print '>>Check you have set up the db and user correctly as per the README!<<'
        sys.exit(1)
    except IOError as e:
        print 'I/O Error %d: %s' % (e.args[0],e.args[1])
        print '>>Check you have connected all sensors correctly!<<'
        sys.exit(1)
    finally:
        if con:
            con.close()

