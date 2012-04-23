#!/bin/bash

uri=$1
basedn=$2
anonymous=$3
basedngroup=$4
binddn=$5
bindpw=$6

ldapconf=/etc/sssd/sssd.conf
bakconf=/etc/sssd/sssd.conf.gecos-firststart.bak
tmpconf=/tmp/sssd.conf.tmp
firstbootconfdir=/usr/share/firstboot/

#bakdir=/usr/share/firstboot/pamd-ldap.bak
#pamd=/etc/pam.d/
#nsswitch=/etc/nsswitch.conf



# Need root user
need_root() {
    if [ 0 != `id -u` ]; then
        echo "You must be root to run this script."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    
# packages: sssd libnss-sss libpam-sss auth-client-config
    
    for pkg in sssd libnss-sss libpam-sss auth-client-config
    do
     dpkg -l $pkg | grep ii
     if [ $? != 0 ]; then 
        DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive apt-get install $pkg -y --assume-yes --force-yes

        if [ $? != 0 ]; then
             echo "ERROR: installing $pkg"
          exit 1
        fi
      fi
    done  

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

    auth-client-config -a -r -p sssd
    mv $ldapconf $ldapconf".bak"
    mv $bakconf $ldapconf
    cp -r /etc/init/dbus.conf.gecos-bak /etc/init/dbus.conf

    DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive apt-get remove sssd libpam-sss libnss-sss -y --assume-yes --force-yes
    result=$?

    if [ "$result" != 0 ]; then
        echo "ERROR: uninstalling PAM SSS packages"
        exit 1
    fi

    echo 0
}

# Make a backup
backup() {
    if [ ! -f $bakconf ]; then
        cp $ldapconf $bakconf
    fi
}


# Update the configuration
update_conf() {

    check_prerequisites
    backup

    cp -r $firstbootconfdir/sssd.conf $ldapconf
    if [ $anonymous -ne 1 ]; then
        sed -e s@"^ldap_uri = .*"@"ldap_uri $uri"@ \
            -e s/"^ldap_search_base = .*"/"ldap_search_base $basedn"/g \
            -e s/"^ldap_user_search_base = .*"/"ldap_user_search_base $basedn"/g \
            -e s/"^ldap_group_search_base = .*"/"ldap_group_search_base $basedngroup"/g \
            -e s/"^ldap_binddn = .*"/"ldap_binddn $binddn"/g \
            -e s/"^ldap_bindpw = .*"/"ldap_bindpw $bindpw"/g \
            $ldapconf > $tmpconf
    else
        sed -e s@"^ldap_uri = .*"@"ldap_uri $uri"@ \
            -e s/"^ldap_search_base = .*"/"ldap_search_base $basedn"/g \
            -e s/"^ldap_user_search_base = .*"/"ldap_user_search_base $basedn"/g \
            -e s/"^ldap_group_search_base = .*"/"ldap_group_search_base $basedngroup"/g \
            -e s/"^ldap_binddn = .*"/"#ldap_binddn $binddn"/g \
            -e s/"^ldap_bindpw = .*"/"#ldap_bindpw $bindpw"/g \
            $ldapconf > $tmpconf
    fi


    mv $tmpconf $ldapconf
    chmod 600 $ldapconf
    cp -r $firstbootconfdir/acc-sssd /etc/auth-client-config/profile.d/
    auth-client-config -a -p sssd
    service sssd restart
    cp -r /etc/init/dbus.conf /etc/init/dbus.conf.gecos-bak
    cp -r $firstbootconfdir/dbus.conf /etc/init/
    echo "Configuration updated successfully."

    exit 0
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
