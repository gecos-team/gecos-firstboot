#!/bin/bash

lang=$1
appname="firstboot"

if [ "" == "$lang" ]; then
    lang="es"
fi

podir="../po"
pofile="${podir}/${lang}.po"
mofile="${podir}/${appname}.mo"

msgfmt $pofile --output-file $mofile
