#!/usr/bin/bash
ble-serial -d DC:FE:4D:6F:9C:F2 -w 0000fff2-0000-1000-8000-00805f9b34fb -r 0000fff1-0000-1000-8000-00805f9b34fb -v -b -k ./ELM327.log -p /etc/RFCOMM1 2>ELM327cat.log &

