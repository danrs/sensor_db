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


# Set up read functions for use by data source objects
def read_heartrate(self):
    value = self.hardware.read()
    return value

def read_gas():
    return 0

read_functions = {}
read_functions['heartrate'] = read_heartrate
read_functions['gas'] = read_gas

def get_hw_heartrate():
    return heartsense.heartsense()

get_hardware = {}
get_hardware['heartrate'] = get_hw_heartrate


class source:
    def __init__(self, cursor, name):
        self.cursor = cursor
        self.name = name
        self.read = read_functions[self.name]
        self.hardware = get_hardware[self.name]


if __name__ == '__main__':
    print 'Connecting to database'
    try:
        con = mdb.connect(dbhost, dbuser, dbpword, dbname);
        cur = con.cursor()
        dbinit(cur)
        cur.execute('SHOW TABLES')
        print cur.fetchall()
        foo = source(cur, 'heartrate')
        print foo.read()
    except mdb.Error, e:
        print 'Error %d: %s' % (e.args[0],e.args[1])
        print '>>Check you have set up the db and user correctly as per the README!<<'
        sys.exit(1)
    finally:
        if con:
            con.close()

