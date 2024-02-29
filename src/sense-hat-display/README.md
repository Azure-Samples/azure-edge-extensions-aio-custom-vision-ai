# Azure IoT Operations (AIO) Sense Hat Display module

This container is an dapr workload that gets messages from the MQ broker and blinks the raspberry Pi's senseHat according to the tags specified in the inputs messages. This module is written in python and requires a [SenseHat](https://www.raspberrypi.org/products/sense-hat/) to work. The amd64 template does not include this module since it is a raspberry pi only device.

It is a Linux Docker container made for ARM processors written in Python.