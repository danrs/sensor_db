#!/usr/bin/python

# Import sensor/actuator libraries
import Adafruit_BMP.BMP085 as BMP085 #BMP085/BMP180 temperature and humdity sensor
import python_uart_gps as uart_gps
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
    cursor.execute("""CREATE TABLE IF NOT EXISTS imu (time TIMESTAMP, temperature INTEGER,
                      ax INTEGER, ay INTEGER, az INTEGER,
                      wx INTEGER, wy INTEGER, wz INTEGER,
                      mx INTEGER, my INTEGER, mz INTEGER);""")
    cursor.execute('CREATE TABLE IF NOT EXISTS gas (time TIMESTAMP, raw_value INTEGER);')
    cursor.execute("""CREATE TABLE IF NOT EXISTS gps (time TIMESTAMP, gps_time TIMESTAMP,
                      satellites INTEGER, fix INTEGER, latitude DOUBLE, north_south CHAR(1),
                      longitude DOUBLE, east_west CHAR(1), altitude DOUBLE);""")
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
    except mdb.Error as e:
        print 'Database Error %d: %s' % (e.args[0],e.args[1])
        print '>>Check you have set up the db and user correctly as per the README!<<'
        sys.exit(1)

    print 'Setting up sensors'
    ignore = {}
    motor1 = v_m.vibration_motor("P9_17")   # connect to I2C1 connector
    motor2 = v_m.vibration_motor("P9_26")   # connect to UART1 connector
    gas_sensor = mq5.mq5()                  # AIN0 is default pin
    try:
        gps_sensor = uart_gps.uart_gps() # UART1 bus
        ignore['gps'] = False
    except IOError as e:
        print 'GPS sensor not connected, ignoring sensor'
        ignore['gps'] = True
    try:
        heart_sensor = heartsense.heartsense()  # I2C2 bus
        ignore['heart_sensor'] = False
    except IOError as e:
        print 'Heart rate sensor not connected, ignoring sensor'
        ignore['heart_sensor'] = True
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

    # read sensors and store data in db
    try:
        print('Starting main loop reading sensors into db')
        while True:
            cur.execute('INSERT INTO motors (time, m1_status, m2_status) VALUES(%s,%s,%s)',
                        (time.strftime('%Y-%m-%d %H:%M:%S'),motor1.status,motor2.status))
            cur.execute('INSERT INTO gas (time, raw_value) VALUES(%s,%s)',
                        (time.strftime('%Y-%m-%d %H:%M:%S'),gas_sensor.read_raw()))
            if not ignore['gps']:
                gps_data = gps_sensor.read()
                gps_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(gps_data['time'])))
                cur.execute("""INSERT INTO gps (time,gps_time,satellites,fix,latitude,north_south,
                               longitude,east_west,altitude) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (time.strftime('%Y-%m-%d %H:%M:%S'),gps_time,gps_data['sats'],
                             gps_data['fix'],gps_data['lat'],gps_data['lat_ns'],gps_data['lon'],
                             gps_data['lon_ew'],gps_data['altitude']))
            if not ignore['heart_sensor']:
                cur.execute('INSERT INTO heartrate (time, bpm) VALUES(%s,%s)',
                            (time.strftime('%Y-%m-%d %H:%M:%S'),heart_sensor.read()))
            if not ignore['imu_sensor']:
                imu_data = imu_sensor.read_all()
                cur.execute("""INSERT INTO imu (time,temperature,ax,ay,az,wx,wy,wz,mx,my,mz)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (time.strftime('%Y-%m-%d %H:%M:%S'),imu_data[0],imu_data[1],imu_data[2],imu_data[3],
                             imu_data[4],imu_data[5],imu_data[6],imu_data[7],imu_data[8],imu_data[9]))
            if not ignore['bmp_sensor']:
                cur.execute('INSERT INTO environment (time, temperature, pressure, altitude) VALUES(%s,%s,%s,%s)',
                            (time.strftime('%Y-%m-%d %H:%M:%S'),bmp_sensor.read_temperature(),
                              bmp_sensor.read_pressure(), bmp_sensor.read_altitude()))

            con.commit()
            time.sleep(0.5)
            print('repeating')
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

