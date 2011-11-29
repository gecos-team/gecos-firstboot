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
    if [ $(check_backup) -eq 1 ]; then
        return 1
    else
        return 0
    fi
    exit 0
}

# Restore the configuration
restore() {

    if [ $(check_backup) -lt 1 ]; then
        echo "Not found: "$bakdir
        exit 1
    fi
    mv $bakdir/nsswitch.conf $nsswitch
    mv $bakdir $pamd
    rm -rf $bakdir 
    domainjoin-cli leave    
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail to restore AD configuration"
        exit 1
    fi

    exit 0
}

# Make a backup
check_backup(){
    if [ ! -d $bakdir ]; then
        return 0
    else
        return 1
    fi
}

backup() {
    if [ $(check_backup) -lt 1 ]; then
        mkdir $bakdir
        cp -r $pamd/common-* $bakdir
    else
        cp -r $pamd/common-* $bakdir
    fi
}

# Update the configuration
update_conf() {

    check_prerequisites
    backup
    echo $dns > $resolv_header

    domainjoin-cli join $fqdn $user $passwd
    retval=$(echo $?)
    if [ $retval -ne 0 ]; then
        echo "Fail connecting to AD"
        restore
        exit 1
    fi
    $likewiseconf AssumeDefaultDomain true
    rm -rf $pamd/common-*
    debconf-set-selections $debconffile
    pam-auth-update --package --force
    cp $nsswitch $bakdir
    sed -i 's|ldap||g' $nsswitch
    
echo "The configuration was updated successfully."
    exit 0
}


# Restore or update the Chef configuration
case $fqdn in
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
