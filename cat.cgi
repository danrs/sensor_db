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
import Cookie
from base64 import b64encode

# Import other stuff we need
import MySQLdb as mdb
import sys
import time
import db_config # database settings from ./db_config.py

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
script_uri = "http://" + os.environ['HTTP_HOST'] + os.environ['SCRIPT_NAME']
root_url = re.sub("/love2041[.]cgi.*$", "", script_uri)
path_info = ""
if 'PATH_INFO' in os.environ:
    path_info = os.environ['PATH_INFO']
    if(path_info == "/"):  #ignore a trailing slash
        os.environ['PATH_INFO'] = ""
        path_info = os.environ['PATH_INFO']

form = cgi.FieldStorage()
username = form.getfirst("user", "")
search = form.getfirst("search","")
last_page=False
login_name = form.getfirst("login_name", "")
password = form.getfirst("password", "")
logout = form.getfirst("logout", "")
edit_profile=form.getfirst("edit_profile","")
current_page=form.getfirst("current_page","")


#print html header
print "Content-Type: text/html\r\n"

#print relevant page
if (True):
#   #login page
    t = env.get_template('page_not_found.html')
    print t.render(script_uri=script_uri, root=root_url)
elif ""!=form.getfirst("e_password",""):
#   #profile edit page
#   #I need some consistency with chosing how to load pages
#   #should have used a hidden variable to track "state"
    badPassword= not db.check_login(current_user, form.getfirst("e_password",""))
    badPasswordMatch=False
    if not badPassword:
        password1=form.getfirst("e_new_password1","")
        password2=form.getfirst("e_new_password2","")
        if(password1==password2 and password1!=""):
            db.update_student(current_user, form)
        else:
            badPasswordMatch=True
    t = env.get_template('edit_profile.html')
    student = db.getStudent(current_user)
    print t.render(script_uri=script_uri, root=root_url,badPassword=badPassword, student=student, badPasswordMatch=badPasswordMatch)
elif edit_profile=="1":
#   #edit profile of logged in user
    t = env.get_template('edit_profile.html')
    student = db.getStudent(current_user)
    print t.render(script_uri=script_uri, root=root_url,badPassword=False, student=student)
elif username != "":
#   #print a profile
    student = db.getStudent(username)
    if student is None:
        t = env.get_template('profile_not_found.html')
        print t.render(script_uri=script_uri, root=root_url)
    else:
        t = env.get_template('profile.html')
        print t.render(script_uri=script_uri, root=root_url, student=student)
elif search != "":
#   #search for users by username
    t = env.get_template('search.html')
    page=int(form.getfirst("page", 1))
    usernames = db.search(search, thumbs_per_page*(page-1), thumbs_per_page)
#   #determine if we have reached end of dataset
    if(len(usernames)==0):
        page=page-1
        usernames = db.search(search, thumbs_per_page*(page-1), thumbs_per_page)
        last_page=True
    elif(len(usernames)<thumbs_per_page):
        last_page=True
    students = []
    for name in usernames:
        students.append(db.getStudent(name))
    print t.render(script_uri=script_uri, root=root_url, users=students, 
            page=page, path_info=path_info, search=search, last_page=last_page)
elif path_info == '':
#   #print home page (12 random users needed)
    t = env.get_template('home.html')
    users=db.getRandomUserNames(thumbs_per_page)
    print t.render(users=users, script_uri=script_uri, root=root_url)
elif path_info == '/about':
#   #about page
    t = env.get_template('about.html')
    print t.render(script_uri=script_uri, root=root_url)
elif path_info == '/browse':
#   #browse 12 users per page (alphabetical)
    t = env.get_template('browse.html')
    page = int(form.getfirst("page",1))
    users=db.browse_users(thumbs_per_page*(page-1), thumbs_per_page)
    if(len(users)==0):
        page=page-1
        users = db.browse_users(thumbs_per_page*(page-1), thumbs_per_page)
        last_page=True
    elif(len(users)<thumbs_per_page):
        last_page=True
    print t.render(script_uri=script_uri, root=root_url, page=page, 
            users=users, path_info=path_info, last_page=last_page)
elif path_info == '/match':
#   #match page
    t = env.get_template('match.html')
    page = int(form.getfirst("page", 1))
    users=db.match_users(thumbs_per_page*(page-1), thumbs_per_page, current_user)
    if(len(users)==0):
        page=page-1
        users = db.match_users(thumbs_per_page*(page-1), thumbs_per_page, current_user)
        last_page=True
    elif(len(users)<thumbs_per_page):
        last_page=True
    print t.render(script_uri=script_uri, root=root_url, page=page,
            users=users, path_info=path_info, last_page=last_page)
else:
#   #no page present
    t = env.get_template('page_not_found.html')
    print t.render(script_uri=script_uri, root=root_url)
