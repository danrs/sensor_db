#!/usr/bin/python

# Script to display server data and motor controls on a web page
# Should not be run as root, to avoid security issues.


# Import other stuff we need
import MySQLdb as mdb
import sys
import time
import db_config # database settings from ./db_config.py


