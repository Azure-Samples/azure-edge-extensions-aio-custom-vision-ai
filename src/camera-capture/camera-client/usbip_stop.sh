#!/bin/bash

# Locate usbip
usbip_path=$(which usbip)

# Check if usbip is valid
if [ -z "$usbip_path" ]; then
    echo "usbip not found. Please install it and make sure it's in your PATH."
    exit 1
fi

# Detach all shared usb devices
$usbip_path detach --port=$($usbip_path port | grep '<Port in Use>' | sed -E 's/^Port ([0-9][0-9]).*/\1/')