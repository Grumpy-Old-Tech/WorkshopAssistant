#!/usr/bin/env python

import requests
from Talker import say

#IP Address of ESP
ip='xxxxxxxxxxxx'

#Declaration of ESP names
devname=('Device 1', 'Device 2', 'Device 3')
devid=('/Device1', '/Device2', '/Device3')


#ESP6266 Devcies control
def ESP(phrase):
    for num, name in enumerate(devname):
        if name.lower() in phrase:
            dev=devid[num]
            if 'on' in phrase:
                ctrl='=ON'
                say("Turning On " + name)
            elif 'off' in phrase:
                ctrl='=OFF'
                say("Turning Off " + name)
            rq = requests.head("https://"+ip + dev + ctrl)
