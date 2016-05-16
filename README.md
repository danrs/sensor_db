# sensor database
Repository for python script(s) to dump Grove sensor data into a database

## Setup
If you don't already have mysql installed, install it with:
```
$ sudo apt-get install mysql-server
```

You can then install the python plugin:
```
$ sudo apt-get install python-mysqldb
```

Once this is done, you will need to create a database and user for the
scripts in this repository to use. The default database is "catdb" and the
default user:password is "cat:cat". You can create the db and user as follows:
```
$ mysql -u root -p          # login to mysql
mysql> CREATE DATABASE catdb;    # create the database
mysql> CREATE USER 'cat'@'localhost' IDENTIFIED BY 'cat'; # create the user
mysql> USE catdb;
mysql> GRANT ALL ON catdb.* TO 'cat'@'localhost'; # give the user access to the db
mysql> quit # we are done here
```

Finally, you will need to install libraries for each of the sensors used in the
logging script. Repositories for each sensor are as follows:
https://github.com/danrs/python_uart_gps
https://github.com/danrs/python_i2c_mpu9250
https://github.com/danrs/python_i2c_heart_rate_sensor
https://github.com/danrs/python_mq5_gas_sensor
https://github.com/danrs/python_vibration_motor
https://github.com/adafruit/Adafruit_Python_BMP.git
Install these sensor libraries according to the instructions in their READMEs.

## Using the Sensor Logging Script
Now you are ready to begin using this repository. To run the sensor logging script:
```
python sensor_db.py
```

This script will create tables and insert data from all the sensor mentioned above.
If an I2C of UART sensor is not connected when the script starts, this sill be
noted and the sensor ignored (analog sensors can't be ignored as there's no way to
tell if they are connected).

## Using the Web Interface
The web interface s a simple CGI interface which shows the latest database info
and allows the database info to be downloaded as csv.
To set up the web scripts, do the following:
```
./web-setup.sh
```

This will set the correct permissions and copy the web content to /usr/lib/cgi-bin,
so you can access it in your browser at:

http://<beaglebone-ip>:8080/cgi-bin/sensor_db/cat.cgi

Note that if you change any web code, you will need to re-run web-setup.sh to copy the
changed files across. If this is inconvenient, you can simlink the web directory instead
using "./web-setup.sh -s", but the you will need to make sure the permissions on all
parent directories of are correct. This may be insecure and is recommended only for
developers working on safe (non-public) networks.


### Changing database settings
If you need to modify the database connection settings, see the file db_config.py.


Written by Daniel Smith for UNSW Australia and LaTrobe University. MIT license and all text above must be included in any redistribution

