#!/bin/bash

uri=$1
basedn=$2
basedngroup=$3
anonymous=$4
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
    
    installed_libnss_ldapd=`dpkg -l | grep libnss-ldapd`
    installed_nslcd=`dpkg -l | grep nslcd`
    installed_libnss_ldapd=`dpkg -l | grep libpam-ldapd`

    if [ $installed_libnss_ldapd -ne 0 -o $installed_nslcd -ne 0 -o $installed_libnss_ldapd -ne 0 ]; then

        result=`DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive apt-get install libnss-ldapd nslcd libpam-ldapd -y --assume-yes --force-yes`      
        if [ $result -ne 0 ]; then
            echo "Impossible install libnss-ldapd nslcd libpam-ldapd packges"
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

    if [ "" == "$basedngroup" ]; then
        echo "Base DN Group couldn't be empty."
        exit 1
    fi

    if [ "" == "$binddn" ]; then
        echo "Bind DN couldn't be empty."
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
    mv $bakdir/* $pamd/
    rm -rf $bakdir
    exit 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $ldapconf $bakconf
    fi
    if [ ! -d $bakdir ]; then
        mkdir $bakdir
        cp -r $pamd/* $bakdir
        cp $nsswitch $bakdir
    else
        cp -r $pamd/* $bakdir
        cp $nsswitch $bakdir
    fi

}


# Update the configuration
update_conf() {

    check_prerequisites
    backup

    cp -r $pamdconfig/nslcd.conf $ldapconf
    if [ $anonymous -ne 0 ]; then
        sed -e s@"^uri .*"@"uri $uri"@ \
            -e s/"^base .*"/"base $basedn"/g \
            -e s/"^nss_base_group .*"/"nss_base_group $basedngroup"/g \
            -e s/"^binddn .*"/"binddn $binddn"/g \
            -e s/"^bindpw .*"/"bindpw $bindpw"/g \
            $ldapconf > $tmpconf
    else
        sed -e s@"^uri .*"@"uri $uri"@ \
            -e s/"^base .*"/"base $basedn"/g \
            -e s/"^nss_base_group .*"/"nss_base_group $basedngroup"/g \
            -e s/"^binddn .*"/"#binddn"/g \
            -e s/"^bindpw .*"/"#bindpw"/g \
            $ldapconf > $tmpconf
    fi

    # It's posible that some options are commented,
    # be sure to decomment them.
    if [ $anonymous -ne 0 ]; then
        sed -e s@"#^uri .*"@"uri $uri"@ \
            -e s/"#^base .*"/"base $basedn"/g \
            -e s/"#^nss_base_group .*"/"nss_base_group $basedngroup"/g \
            -e s/"#^binddn .*"/"binddn $binddn"/g \
            -e s/"#^bindpw .*"/"bindpw $bindpw"/g \
            $tmpconf > $tmpconf".2"
    else
        sed -e s@"^#uri .*"@"uri $uri"@ \
            -e s/"^#base .*"/"base $basedn"/g \
            -e s/"^#nss_base_group .*"/"nss_base_group $basedngroup"/g \
            -e s/"^binddn .*"/"#binddn"/g \
            -e s/"^bindpw .*"/"#bindpw"/g \
            $tmpconf > $tmpconf".2"
    fi
        -e s/"^#bindpw .*"/"bindpw $bindpw"/g \
        $tmpconf > $tmpconf".2"

    mv $tmpconf".2" $tmpconf

    check_configuration

    mv $tmpconf $ldapconf
    cp -r $pamdconfig/pam.d/* $pamd
    cp -r $pamdconfig/nsswitch.conf $nsswitch
    service nslcd restart
    echo "The configuration was updated successfully."

    exit 0
}

# Check the changes are valid
check_configuration() {
    r_uri=`egrep "^uri $uri" $tmpconf`
    r_base=`egrep "^base $basedn" $tmpconf`
    r_base=`egrep "^nss_base_group $basedngroup" $tmpconf`
    r_bind=`egrep "^binddn $binddn" $tmpconf`
    r_pass=`egrep "^bindpw $bindpw" $tmpconf`

    if [ "" == "$r_uri" -o "" == "$r_base"  ]; then
        restore
        echo "The configuration couldn't be updated correctly."
        exit 1
    fi
    if [ $anonymous -eq 1 ]; then

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
