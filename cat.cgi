#!/usr/bin/python

# CAT web interface (cgi)
# Should not be run as root, to avoid security issues.

#import things we need
import cgi
import csv
import db_config # database settings from ./db_config.py
import jinja2
from jinja2 import Environment, FileSystemLoader
import MySQLdb as mdb
import os
import re
import socket
import StringIO
import sys
import time

#debugging
import cgitb
cgitb.enable()
sys.stderr = sys.stdout


##########################
#main program starts here#
##########################

#load template with jinja2
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)

#set up a socket for talking with the motor control script (sensor_db.py)
HOST = '127.0.0.1'
PORT = 16001  #motor
motor_socket = socket.socket()

#get environment and form variables
form = cgi.FieldStorage()
script_uri = "http://" + os.environ['HTTP_HOST'] + os.environ['SCRIPT_NAME']
root_url = re.sub("/cat[.]cgi.*$", "", script_uri)
path_info = ""
if 'PATH_INFO' in os.environ:
    path_info = os.environ['PATH_INFO']
    if(path_info == "/"):  # ignore trailing slash
        os.environ['PATH_INFO'] = ""
        path_info = os.environ['PATH_INFO']
    path_info = re.sub('^/*','',path_info) # remove leading slashes

sensor_list=['motor','gas','gps','heartrate','imu','environment']
csv_regex = re.compile(r'(?P<sensor>[^/]+)/csv')
csv_match = csv_regex.match(path_info)

#print html header
print "Content-Type: text/html\r\n"

#print relevant page
if path_info == '':
#   #home page
    t = env.get_template('home.html')
    print t.render(sensor_list=sensor_list, script_uri=script_uri, root=root_url)
elif path_info == 'about':
#   #about page
    t = env.get_template('about.html')
    print t.render(sensor_list=sensor_list,script_uri=script_uri, root=root_url)
elif path_info in sensor_list:
#   #sensor page
    sensor = path_info
    table_length = 20 #default number of rows to print
    con = mdb.connect(db_config.dbhost, db_config.dbuser, db_config.dbpword, db_config.dbname);
    cur = con.cursor()
    query_string = 'SHOW columns FROM ' + sensor # get column names
    cur.execute(query_string)
    table_head = [column[0] for column in cur.fetchall()]
    table_data = []
    query_string = ('SELECT * FROM (SELECT * FROM ' + sensor + ' ORDER BY time DESC LIMIT '
                    + str(table_length) + ') AS TEMP ORDER BY TIME ASC') # get last table_length rows of data
    cur.execute(query_string)
    for row in cur.fetchall():
        table_data.append(row)
    if sensor == "motor":
        vibrate = form.getfirst("vibrate","")
        if vibrate == "1" or vibrate == "2":
            try:
                motor_socket.connect((HOST, PORT))
                motor_socket.send(vibrate)
                motor_socket.close()
                status_message = 'Motor ' + vibrate + ' was vibrated for one second'
                alert = 'success'
            except IOError as e:
                status_message = 'Could not connect to motor script'
                alert = 'warning'
        else:
            status_message = ''
            alert = ''
        t = env.get_template('motor.html')
        print t.render(motor_status=status_message,alert=alert,
                       table_head=table_head,table_data=table_data,
                       sensor_list=sensor_list,sensor=sensor,script_uri=script_uri,root=root_url)
    else:
        t = env.get_template('sensor.html')
        print t.render(table_head=table_head,table_data=table_data,
                       sensor_list=sensor_list,sensor=sensor,script_uri=script_uri,root=root_url)
elif csv_match:
#   # print raw csv
    sensor = csv_match.group('sensor')
    con = mdb.connect(db_config.dbhost, db_config.dbuser, db_config.dbpword, db_config.dbname);
    cur = con.cursor()
    io = StringIO.StringIO()
    c = csv.writer(io)
    query_string = 'SHOW columns FROM ' + sensor # get column names
    cur.execute(query_string)
    c.writerow([column[0] for column in cur.fetchall()]) #write to csv
    query_string = 'SELECT * FROM ' + sensor # get actual data
    cur.execute(query_string)
    c.writerows(cur.fetchall()) #write to csv
    print re.sub('\n','<br>\n',io.getvalue()) # add in <br> on newlines and print
else:
#   #no page present
    t = env.get_template('page_not_found.html')
    print t.render(sensor_list=sensor_list,script_uri=script_uri, root=root_url)
