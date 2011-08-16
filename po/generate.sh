#!/bin/bash

lang=$1
appname="firstboot"

if [ "" == "$lang" ]; then
    lang="es"
fi

potfilesin="./POTFILES.in"
potfile="./${appname}.pot"
pofile="./${lang}.po"
pofilemerged="./${lang}.merged.po"
mofile="./${appname}.mo"

find ../ -type f -name "*.py" > $potfilesin

xgettext --language=Python --keyword=_ --output=$potfile -f $potfilesin

if [ ! -f $pofile ]; then

    msginit --input=$potfile --locale=es_ES --output-file $pofile
    
else

    msgmerge $pofile $potfile > $pofilemerged
    mv $pofilemerged $pofile

fi

msgfmt $pofile --output-file $mofile
