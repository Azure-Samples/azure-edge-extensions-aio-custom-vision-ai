#!/bin/bash

# Input parameters
server_IP_address=$1
shift
usb_ids=("$@")

# Add symbolic link for host's usb.ids (TODO: this might not be needed) 
mkdir -p /usr/share/hwdata/
ln -s /usr/share/misc/usb.ids /usr/share/hwdata/usb.ids

# This script enables the vhci-hcd for current running kernel
if modprobe vhci-hcd && echo 'vhci-hcd' >> /etc/modules; then
    for usb_id in "${usb_ids[@]}"; do
        if ./usbip_start.sh "$server_IP_address" "$usb_id"; then
            echo "usbip_start.sh operation successful for usb_id: $usb_id."
        else
            echo "usbip_start.sh operation failed for usb_id: $usb_id."
        fi
    done
else
    echo "Installation operation failed."
    exit 1
fi