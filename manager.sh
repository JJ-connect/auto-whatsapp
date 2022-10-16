#!/bin/sh
echo 'manager shell wait'
sleep 5 # wait 5 seconds
#sleep 1m # wait 1 minute
echo 'manager shell wait over'
/usr/bin/python3 /home/admin/Desktop/whatsapp-sender/whatsapp.py >> out.txt
echo 'python complete'
