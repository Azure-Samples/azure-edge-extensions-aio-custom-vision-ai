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

# Unbind a usb device
if $usbip_path unbind --$($usbip_path list -p -l | grep '#usbid='$usb'#' | cut '-d#' -f1); then
    killall usbipd
    echo "Unbind operation on $usb was successful."
else
    echo "Unbind operation on $usb failed."
fi