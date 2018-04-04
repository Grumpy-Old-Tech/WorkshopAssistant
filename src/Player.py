#!/usr/bin/env python

#This is different from AIY Kit's actions
#Copying and Pasting AIY Kit's actions commands will not work


import os
import os.path
import subprocess
import json
import re
import psutil

from Talker import say


#Function to check if Player is playing
def isPlayerPlaying():
    mpvactive = False
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if 'mpv'in p.name():
            mpvactive = True
            break
    return mpvactive

#Function to manage player start volume
def setPlayerStartVolume():
    if os.path.isfile("/home/pi/.mediavolume.json"):
        with open('/home/pi/.mediavolume.json', 'r') as vol:
            oldvollevel = json.load(vol)
        print(oldvollevel)
        startvol=oldvollevel
    else:
        startvol=50
    return startvol

#Function to stop player
def stopPlayer():
    pkill = subprocess.Popen(["/usr/bin/pkill","mpv"],stdin=subprocess.PIPE)

#Function to pause player
def pausePlayer(phase):
    if isPlayerPlaying():
        playstatus=os.system("echo '"+json.dumps({ "command": ["set_property", "pause", True]})+"' | socat - /tmp/mpvsocket")
    else:
        say("Sorry nothing is playing right now")


#Function to pause player
def resumePlayer(phase):
    if isPlayerPlaying():
        playstatus=os.system("echo '"+json.dumps({ "command": ["set_property", "pause", False]})+"' | socat - /tmp/mpvsocket")
    else:
        say("Sorry nothing is playing right now")

#Function to get old volume level
def getVolumeLevel():
    if os.path.isfile("/home/pi/.mediavolume.json"):
        with open('/home/pi/.mediavolume.json', 'r') as vol:
            oldvollevel = json.load(vol)
            for oldvollevel in re.findall(r'\b\d+\b', str(oldvollevel)):
                oldvollevel=int(oldvollevel)
    else:
        mpvgetvol=subprocess.Popen([("echo '"+json.dumps({ "command": ["get_property", "volume"]})+"' | socat - /tmp/mpvsocket")],shell=True, stdout=subprocess.PIPE)
        output=mpvgetvol.communicate()[0]
        for oldvollevel in re.findall(r"[-+]?\d*\.\d+|\d+", str(output)):
            oldvollevel=int(oldvollevel)

    return oldvollevel


#Function to increase volume
def increaseVolume(phase):
    oldvollevel = getVolumeLevel()
    if any(char.isdigit() for char in phase):
        for changevollevel in re.findall(r'\b\d+\b', phase):
            changevollevel=int(changevollevel)
    else:
        changevollevel=10
    newvollevel= oldvollevel+ changevollevel
    print(newvollevel)
    if newvollevel>100:
        settingvollevel==100
    elif newvollevel<0:
        settingvollevel==0
    else:
        settingvollevel=newvollevel
    with open('/home/pi/.mediavolume.json', 'w') as vol:
        json.dump(settingvollevel, vol)
    mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(settingvollevel)]})+"' | socat - /tmp/mpvsocket")
            
#Function to decrease volume
def decreaseVolume(phase):
    oldvollevel = getVolumeLevel()
    if any(char.isdigit() for char in phase):
        for changevollevel in re.findall(r'\b\d+\b', phase):
            changevollevel=int(changevollevel)
    else:
        changevollevel=10
    newvollevel= oldvollevel - changevollevel
    print(newvollevel)
    if newvollevel>100:
        settingvollevel==100
    elif newvollevel<0:
        settingvollevel==0
    else:
        settingvollevel=newvollevel
    with open('/home/pi/.mediavolume.json', 'w') as vol:
        json.dump(settingvollevel, vol)
    mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(settingvollevel)]})+"' | socat - /tmp/mpvsocket")

#Function to set discrete volume level
def setDiscreteVolume(phase):
    if 'hundred' in phase or 'maximum' in phase:
        settingvollevel=100
        with open('/home/pi/.mediavolume.json', 'w') as vol:
            json.dump(settingvollevel, vol)
        mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(settingvollevel)]})+"' | socat - /tmp/mpvsocket")
        say("Volume set to maximum")
 
    elif 'zero' in phase or 'minimum' in phase:
        settingvollevel=0
        with open('/home/pi/.mediavolume.json', 'w') as vol:
            json.dump(settingvollevel, vol)
        mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(settingvollevel)]})+"' | socat - /tmp/mpvsocket")
        say("Volume set to minimum")

    else:
        for settingvollevel in re.findall(r"[-+]?\d*\.\d+|\d+", phase):
            with open('/home/pi/.mediavolume.json', 'w') as vol:
                json.dump(settingvollevel, vol)
        mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(settingvollevel)]})+"' | socat - /tmp/mpvsocket")
        say("Volume set to " + settingvollevel)

#Function to control Player volume
def controlPlayerVolume(phase):
    if isPlayerPlaying():
        if 'set' in phase:
            setDiscreteVolume(phase)

        elif 'change' in phase:
            setDiscreteVolume(phase)

        elif 'increase' in phase:
            increaseVolume(phase)

        elif 'decrease' in phase:
            decreaseVolume(phase)

        elif 'reduce' in phase:
            decreaseVolume(phase)

        else:
            say("Sorry I could not help you")

    else:
        say("Sorry nothing is playing right now")
