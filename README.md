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

Now you are ready to begin using this repository. TODO add instructions on how to run
the script(s) and what it does/they do.
