#!/usr/bin/python

# CAT web interface (cgi)
# Should not be run as root, to avoid security issues.

#import things we need
import re
import cgi
import os
import jinja2
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from base64 import b64encode

# Import other stuff we need
import MySQLdb as mdb
import sys
import time
import db_config # database settings from ./db_config.py
import csv
import StringIO

#debugging
import cgitb; cgitb.enable()
import sys
sys.stderr = sys.stdout


##########################
#main program starts here#
##########################

#load template with jinja2
env = Environment(loader=FileSystemLoader('templates'), autoescape=True)

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
    t = env.get_template('sensor.html')
    print t.render(sensor_list=sensor_list,sensor=path_info, script_uri=script_uri, root=root_url)
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
