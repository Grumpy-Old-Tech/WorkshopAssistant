#!/usr/bin/env python

import requests
import json
from Talker import say


#Initialize colour list
clrlist=[]
clrlistfullname=[]
clrrgblist=[]
clrhexlist=[]
with open('/home/pi/GassistPi/src/colours.json', 'r') as col:
     colours = json.load(col)
for i in range(0,len(colours)):
    clrname=colours[i]["name"]
    clrnameshort=clrname.replace(" ","",1)
    clrnameshort=clrnameshort.strip()
    clrnameshort=clrnameshort.lower()
    clrlist.append(clrnameshort)
    clrlistfullname.append(clrname)
    clrrgblist.append(colours[i]["rgb"])
    clrhexlist.append(colours[i]["hex"])


#Function to get HEX and RGB values for requested colour
def getcolours(phrase):
    usrclridx=idx=phrase.find("to")
    usrclr=query=phrase[usrclridx:]
    usrclr=usrclr.replace("to","",1)
    usrclr=usrclr.replace("'}","",1)
    usrclr=usrclr.strip()
    usrclr=usrclr.replace(" ","",1)
    usrclr=usrclr.lower()
    print(usrclr)
    try:
        for colournum, colourname in enumerate(clrlist):
            if usrclr in colourname:
               RGB=clrrgblist[colournum]
               red,blue,green=re.findall('\d+', RGB)
               hexcode=clrhexlist[colournum]
               cname=clrlistfullname[colournum]
               print(cname)
               break
        return red,blue,green,hexcode,cname
    except UnboundLocalError:
        say("Sorry unable to find a matching colour")


#Function to convert FBG to XY for Hue Lights
def convert_rgb_xy(red,green,blue):
    try:
        red = pow((red + 0.055) / (1.0 + 0.055), 2.4) if red > 0.04045 else red / 12.92
        green = pow((green + 0.055) / (1.0 + 0.055), 2.4) if green > 0.04045 else green / 12.92
        blue = pow((blue + 0.055) / (1.0 + 0.055), 2.4) if blue > 0.04045 else blue / 12.92
        X = red * 0.664511 + green * 0.154324 + blue * 0.162028
        Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
        Z = red * 0.000088 + green * 0.072310 + blue * 0.986039
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        return x,y
    except UnboundLocalError:
        say("No RGB values given")

def hueCheck(phase):
    with open('/home/pi/GassistPi/src/diyHue/config.json', 'r') as config:
        hueconfig = json.load(config)
    for i in range(1,len(hueconfig['lights'])+1):
        try:
            if str(hueconfig['lights'][str(i)]['name']).lower() in phase:
                return i
                break
        except Keyerror:
            say('Unable to help, please check your Hue config file')

    return -1

def hueControl(phrase,lightindex):
    with open('/home/pi/GassistPi/src/diyHue/config.json', 'r') as config:
         hueconfig = json.load(config)
    lightaddress=str(hueconfig['lights_address'][str(lightindex)]['ip'])
    currentxval=hueconfig['lights'][lightindex]['state']['xy'][0]
    currentyval=hueconfig['lights'][lightindex]['state']['xy'][1]
    currentbri=hueconfig['lights'][lightindex]['state']['bri']
    currentct=hueconfig['lights'][lightindex]['state']['ct']
    huelightname=str(hueconfig['lights'][lightindex]['name'])
    try:
        if 'on' in phrase:
            huereq=requests.head("http://"+lightaddress+"/set?light="+lightindex+"&on=true")
            say("Turning on "+huelightname)
        if 'off' in phrase:
            huereq=requests.head("http://"+lightaddress+"/set?light="+lightindex+"&on=false")
            say("Turning off "+huelightname)
        if 'çolor' in phrase:
            rcolour,gcolour,bcolour,hexcolour,colour=getcolours(phrase)
            print(str([rcolour,gcolour,bcolour,hexcolour,colour]))
            xval,yval=convert_rgb_xy(int(rcolour),int(gcolour),int(bcolour))
            print(str([xval,yval]))
            huereq=requests.head("http://"+lightaddress+"/set?light="+lightindex+"&x="+str(xval)+"&y="+str(yval)+"&on=true")
            print("http://"+lightaddress+"/set?light="+lightindex+"&x="+str(xval)+"&y="+str(yval)+"&on=true")
            say("Setting "+huelightname+" to "+colour)
        if 'brightness' in phrase:
            if 'hundred' in phrase or 'maximum' in phrase:
                bright = 100
            elif 'zero' in phrase or 'minimum' in phrase:
                bright = 0
            else:
                bright=re.findall('\d+', phrase)
            brightval= (bright/100)*255
            huereq=requests.head("http://"+lightaddress+"/set?light="+lightindex+"&on=true&bri="+str(brightval))
            say("Changing "+huelightname+" brightness to "+bright+" percent")            
    except (requests.exceptions.ConnectionError,TypeError) as errors:
        if str(errors)=="'NoneType' object is not iterable":
            print("Type Error")
        else:
            say("Device not online")
