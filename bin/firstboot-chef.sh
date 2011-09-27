#!/bin/bash

if [ 0 != `id -u` ]; then
    echo "You must be root to run this script."
    exit 1
fi

