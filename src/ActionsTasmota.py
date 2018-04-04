#!/usr/bin/env python

import requests
from Talker import say


#Sonoff-Tasmota Declarations
#Make sure that the device name assigned here does not overlap any of your smart device names in the google home app
tasmota_devicelist=['Desk Light','Table Light']
tasmota_deviceip=['192.168.1.35','192.168.1.36']


def tasmotaCheck(phase):
    for num, name in enumerate(tasmota_devicelist):
        if name.lower() in phase:
            return num
            break
    return -1

#Function to control Sonoff Tasmota Devices
def tasmotaControl(phrase,num):
    devname = tasmota_devicelist[num]
    devip = tasmota_deviceip[num]
    try:
        if 'on' in phrase:
            rq=requests.head("http://"+devip+"/cm?cmnd=Power%20on")
            say("Tunring on "+devname)
        elif 'off' in phrase:
            rq=requests.head("http://"+devip+"/cm?cmnd=Power%20off")
            say("Tunring off "+devname)
    except requests.exceptions.ConnectionError:
        say("Device not online")