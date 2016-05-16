#!/bin/sh

cgi_path="/usr/lib/cgi-bin"

echo setting permissions
chmod +x .
chmod 711 templates
chmod 755 templates/*
chmod 755 cat.cgi

if [ -z "$1" ]
then
    # Copy web stuff to cgi-bin
    echo "Copying web content to cgi-bin"
    dirpath="$cgi_path/sensor_db"
    mkdir "$dirpath"
    cp cat.cgi "$dirpath/cat.cgi"
    cp db_config.py "$dirpath/db_config.py"
    cp -r templates "$dirpath/templates"
elif [ "$1" = "-s" ]
then
    # symlink web stuff to cgi-bin (less secure)
    echo "symlinking web content to cgi-bin, make sure parent directories have correct permissions"
    ln -s "$(pwd)" "$cgi_path/sensor_db"
else
    # Incorrect script usage
    echo "Usage: ./web-setup.sh [-s]"
fi

echo done!
