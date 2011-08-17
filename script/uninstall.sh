#!/bin/bash


if [ 0 != `id -u` ]; then
    echo "You must be root"
    exit 1
fi

updatedb

for f in `locate firstboot | grep -v home`; do

    if [ -f $f ]; then
        rm -f $f
    elif [ -d $f ]; then
        rm -rf $f
    fi;
    
done
