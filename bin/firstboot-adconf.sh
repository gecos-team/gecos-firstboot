#!/bin/bash

fqdn=$1
dns=$2
user=$3
passwd=$4

resolv=/etc/resolv.conf
resolv_header=/etc/resolvconf/resolv.conf.d/head
likewiseconf=/opt/likewise/bin/lwconfig
bakdir=/opt/likewise/pam.d.bak/
pamd=/etc/pam.d/
debconffile=/opt/likewise/debconf.likewise
nsswitch=/etc/nsswitch.conf
pam_auth_update_orig=/usr/sbin/pam-auth-update
#bakconf=$chefdir/client.rb.gecos-firststart.bak
#tmpconf=/tmp/client.rb.tmp


# Need root user
need_root() {
    if [ 0 != `id -u` ]; then
        echo "You must be root to run this script."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {

    if [ "" == "$fqdn" ]; then
        echo "FQDN couldn't be empty."
        exit 1
    fi

    if [ "" == "$dns" ]; then
        echo "DNS couldn't be empty."
        exit 1
    fi

    if [ "" == "$user" ]; then
        echo "User couldn't be empty."
        exit 1
    fi

    if [ "" == "$passwd" ]; then
        echo "Password couldn't be empty."
        exit 1
    fi
}

# Check if AD is currently configured
check_configured() {
    if [ "$(check_backup)" == "1" ]; then
        echo 1
    else
        echo 0
    fi
    exit 0
}

# Restore the configuration
restore() {

    if [ "$(check_backup)" == "0" ]; then
        echo "Not found: "$bakdir
        mv $pam_auth_update_orig.orig $pam_auth_update_orig
        exit 1
    fi
    mv $bakdir/nsswitch.conf $nsswitch
    mv $bakdir/* $pamd/
    rm -rf $bakdir 
    domainjoin-cli leave    
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail to restore AD configuration"
        mv $pam_auth_update_orig.orig $pam_auth_update_orig
        exit 1
    fi
    mv $pam_auth_update_orig.orig $pam_auth_update_orig

    exit 0
}

# Make a backup
check_backup(){
    if [ ! -d $bakdir ]; then
        echo 0
    else
        echo 1
    fi
}

backup() {
    if [ "$(check_backup)" == "0" ]; then
        mkdir $bakdir
        cp -r $pamd/common-* $bakdir
        cp $nsswitch $bakdir
    else
        cp -r $pamd/common-* $bakdir
        cp $nsswitch $bakdir
    fi
}

# Update the configuration
update_conf() {
    check_prerequisites
    backup
    echo "nameserver $dns" > $resolv_header
    service resolvconf restart
    domainjoin-cli join $fqdn $user $passwd
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    $likewiseconf AssumeDefaultDomain true
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    rm -rf $pamd/common-*
    debconf-set-selections $debconffile 2>&1 |grep -qi "can't open"
    retval=$(echo $?)
    if [ $retval -eq 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    pam-auth-update --package --force
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    sed -i 's|ldap||g' $nsswitch
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    
echo "The configuration was updated successfully."
    mv $pam_auth_update_orig.orig $pam_auth_update_orig
    exit 0
}


# Restore or update the Chef configuration
case $fqdn in
    --restore | -r)
        need_root
        mv $pam_auth_update_orig $pam_auth_update_orig.orig
        cp $pam_auth_update_orig.firstboot $pam_auth_update_orig
        restore
        ;;
    --query | -q)
        check_configured
        ;;
    *)
        need_root
        mv $pam_auth_update_orig $pam_auth_update_orig.orig
        cp $pam_auth_update_orig.firstboot $pam_auth_update_orig
        update_conf
        ;;
esac
