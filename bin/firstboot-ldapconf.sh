#!/bin/bash

uri=$1
basedn=$2
anonymous=$3
basedngroup=$4
binddn=$5
bindpw=$6

ldapconf=/etc/nslcd.conf
bakconf=/etc/nslcd.conf.gecos-firststart.bak
tmpconf=/tmp/nslcd.conf.tmp
debconffile=/usr/share/firstboot/debconf.ldap
pamdconfig=/usr/share/firstboot/pamd-ldap
bakdir=/usr/share/firstboot/pamd-ldap.bak
pamd=/etc/pam.d/
nsswitch=/etc/nsswitch.conf



# Need root user
need_root() {
    if [ 0 != `id -u` ]; then
        echo "You must be root to run this script."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    
    dpkg -l | grep --regexp='ii  libnss-ldapd '
    installed_libnss_ldapd=$?
    dpkg -l | grep --regexp='ii  nslcd '
    installed_nslcd=$?
    dpkg -l | grep --regexp='ii  libpam-ldapd '
    installed_libnss_ldapd=$?
    dpkg -l | grep --regexp='ii  nscd '
    installed_nscd=$?

    if [ "$installed_libnss_ldapd" != 0 -o "$installed_nslcd" != 0 -o "$installed_libnss_ldapd" != 0 -o "$installed_nscd" != 0 ]; then

        DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive apt-get install libnss-ldapd nslcd libpam-ldapd nscd -y --assume-yes --force-yes
        result=$?

        if [ "$result" != 0 ]; then
            echo "Impossible install libnss-ldapd nslcd libpam-ldapd nscd packges"
            exit 1

        fi
    fi

    if [ ! -f $ldapconf ]; then
        echo "File not found: "$ldapconf
        exit 1
    fi

    if [ "" == "$uri" ]; then
        echo "URI couldn't be empty."
        exit 1
    fi

    if [ "" == "$basedn" ]; then
        echo "Base DN couldn't be empty."
        exit 1
    fi



}

# Check if LDAP is currently configured
check_configured() {
    if [ -f $bakconf ]; then
        echo 1
    else
        echo 0
    fi
    exit 0
}

# Restore the configuration
restore() {

    if [ ! -f $bakconf ]; then
        echo "File not found: "$bakconf
        exit 1
    fi

    mv $ldapconf $ldapconf".bak"
    mv $bakconf $ldapconf
    mv $bakdir/nsswitch.conf $nsswitch
    mv $bakdir/nscd.conf /etc/nscd.conf
    mv $bakdir/* $pamd/
    cp -r /etc/init/dbus.conf.gecos-bak /etc/init/dbus.conf
    rm -rf /etc/init/nscd.conf
    rm -rf $bakdir
    DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive apt-get remove libnss-ldapd nslcd libpam-ldapd nscd -y --assume-yes --force-yes
    result=$?

    if [ "$result" != 0 ]; then
        echo "Impossible uninstall libnss-ldapd nslcd libpam-ldapd nscd packges"
        exit 1
    fi

    echo 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $ldapconf $bakconf
    fi
    if [ ! -d $bakdir ]; then
        mkdir $bakdir
        cp -r $pamd/* $bakdir
        cp /etc/nscd.conf $bakdir
        cp $nsswitch $bakdir
    else
        cp -r $pamd/* $bakdir
        cp /etc/nscd.conf $bakdir
        cp $nsswitch $bakdir
    fi

}


# Update the configuration
update_conf() {

    check_prerequisites
    backup

    cp -r $pamdconfig/nslcd.conf $ldapconf
    if [ $anonymous -ne 1 ]; then
        sed -e s@"^uri .*"@"uri $uri"@ \
            -e s/"^base [^group].*"/"base $basedn"/g \
            -e s/"^base group .*"/"base group $basedngroup"/g \
            -e s/"^binddn .*"/"binddn $binddn"/g \
            -e s/"^bindpw .*"/"bindpw $bindpw"/g \
            $ldapconf > $tmpconf
    else
        sed -e s@"^uri .*"@"uri $uri"@ \
            -e s/"^base [^group].*"/"base $basedn"/g \
            -e s/"^base group .*"/"base group $basedngroup"/g \
            -e s/"^binddn .*"/"#binddn"/g \
            -e s/"^bindpw .*"/"#bindpw"/g \
            $ldapconf > $tmpconf
    fi
    # It's posible that some options are commented,
    # be sure to decomment them.
    if [ $anonymous -ne 1 ]; then
        sed -e s@"#^uri .*"@"uri $uri"@ \
            -e s/"#^base [^group].*"/"base $basedn"/g \
            -e s/"#^base group .*"/"base group $basedngroup"/g \
            -e s/"#^binddn .*"/"binddn $binddn"/g \
            -e s/"#^bindpw .*"/"bindpw $bindpw"/g \
            $tmpconf > $tmpconf".2"
    else
        sed -e s@"^#uri .*"@"uri $uri"@ \
            -e s/"^#base [^group].*"/"base $basedn"/g \
            -e s/"^#base group .*"/"base group $basedngroup"/g \
            -e s/"^binddn .*"/"#binddn"/g \
            -e s/"^bindpw .*"/"#bindpw"/g \
            $tmpconf > $tmpconf".2"
    fi

    if [ "" == "$basedngroup" ]; then
        sed -e s/"^base group .*"/"#base group $basedngroup"/g \
            $tmpconf > $tmpconf".2"
    fi

    mv $tmpconf".2" $tmpconf

    check_configuration

    mv $tmpconf $ldapconf
    cp -r $pamdconfig/pam.d/* $pamd
    cp -r $pamdconfig/nsswitch.conf $nsswitch
    cp -r $pamdconfig/nscd.conf /etc/nscd.conf
    cp -r /etc/init/dbus.conf /etc/init/dbus.conf.gecos-bak
    cp -r /usr/share/firstboot/nscd.conf /etc/init/
    cp -r /usr/share/firstboot/dbus.conf /etc/init/
    service nslcd restart
    service nscd restart
    echo "The configuration was updated successfully."

    exit 0
}

# Check the changes are valid
check_configuration() {
    r_uri=`egrep "^uri $uri" $tmpconf`
    r_base=`egrep "^base $basedn" $tmpconf`
    r_base_group=`egrep "^base group $basedngroup" $tmpconf`
    r_bind=`egrep "^binddn $binddn" $tmpconf`
    r_pass=`egrep "^bindpw $bindpw" $tmpconf`

    if [ "" == "$r_uri" -o "" == "$r_base"  ]; then
        restore
        echo "The configuration couldn't be updated correctly."
        exit 1
    fi
    if [ $anonymous -eq 0 ]; then

        if [ "" == "$r_bind" -o "" == "$r_pass"  ]; then
            restore
            echo "The configuration couldn't be updated correctly."
            exit 1
        fi

    fi
}

# Restore or update the LDAP configuration
case $uri in
    --restore | -r)
        need_root
        restore
        ;;
    --query | -q)
        check_configured
        ;;
    *)
        need_root
        update_conf
        ;;
esac
