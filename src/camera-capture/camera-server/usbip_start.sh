#!/bin/bash

# Input parameter
usb=$1

# Locate usbip
usbip_path=$(which usbip)

# Check if usbip is valid
if [ -z "$usbip_path" ]; then
    echo "usbip not found. Please install it and make sure it's in your PATH."
    exit 1
fi

# Bind to a usb device
if $usbip_path bind --$($usbip_path list -p -l | grep '#usbid='$usb'#' | cut '-d#' -f1); then
    echo "Bind operation on $usb was successful."
else
    echo "Bind operation failed on $usb."
    exit 1
fi