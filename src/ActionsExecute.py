#!/usr/bin/env python

import time
import os
from Talker import say


def executeScript(phrase):
    if 'shut down' in phrase:				#Shutdown
        say('OK Shutting down Raspberry Pi')
        time.sleep(10)
        os.system("sudo shutdown -h now")
    if 'reboot' in phrase:				#Reboot
        say('OK Rebooting Raspberry Pi')
        time.sleep(10)
        os.system("sudo shutdown -r now")
    if 'restart' in phrase:				#Restart
        say('OK Restarting Assist on Raspberry Pi')
        time.sleep(10)
        sys.exit