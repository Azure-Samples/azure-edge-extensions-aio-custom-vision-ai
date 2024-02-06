#!/bin/bash

# Input parameters
server=$1
usb=$2

# Locate usbip
usbip_path=$(which usbip)

# Check if usbip is valid
if [ -z "$usbip_path" ]; then
    echo "usbip not found. Please install it and make sure it's in your PATH."
    exit 1
fi

# Attach to a shared usb device
if $usbip_path --debug attach -r $server -b $($usbip_path list -r $server | grep $usb | cut -d: -f1); then
    echo "Successfully attached to usb device: $usb on server: $server."
else
    echo "Failed to attach to usb device: $usb on server: $server."
    exit 1
fi