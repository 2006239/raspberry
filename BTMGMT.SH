#!/bin/bash
sleep 15
sudo btmgmt power off;
sudo btmgmt discov on;
sudo btmgmt le on;
sudo btmgmt bredr off;
sudo btmgmt connectable on;
sudo btmgmt pairable on;
sudo btmgmt power on;
