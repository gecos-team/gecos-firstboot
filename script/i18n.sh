#!/bin/bash

cd ..

lang=$1
appname="firstboot"

if [ "" == "$lang" ]; then
    lang="es"
fi

potfilesin="po/POTFILES.in"
potfile="po/${appname}.pot"
pofile="po/${lang}.po"
pofilemerged="po/${lang}.merged.po"
mofile="po/${appname}.mo"

find . -type f -name "*.py" > $potfilesin

xgettext --language=Python --keyword=_ --output=$potfile -f $potfilesin

if [ ! -f $pofile ]; then

    msginit --input=$potfile --locale=es_ES --output-file $pofile
    
else

    msgmerge $pofile $potfile > $pofilemerged
    mv $pofilemerged $pofile

fi

msgfmt $pofile --output-file $mofile

cd -
