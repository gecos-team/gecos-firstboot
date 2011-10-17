#!/bin/bash

lang=$1
appname="firstboot"

if [ "" == "$lang" ]; then
    lang="es"
fi

podir="../po"
potfilesin="${podir}/POTFILES.in"
potfile="${podir}/${appname}.pot"
pofile="${podir}/${lang}.po"
pofilemerged="${podir}/${lang}.merged.po"
mofile="${podir}/${appname}.mo"

find .. -type f -name "*.py" > $potfilesin

xgettext --language=Python --keyword=_ --output=$potfile -f $potfilesin

if [ ! -f $pofile ]; then

    msginit --input=$potfile --locale=es_ES --output-file $pofile

else

    msgmerge $pofile $potfile > $pofilemerged
    mv $pofilemerged $pofile

fi
