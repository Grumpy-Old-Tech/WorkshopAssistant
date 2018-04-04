#!/usr/bin/env python

import requests
import re
import subprocess
import aftership
import json
import urllib.request
import pafy
import time
from Talker import say


#Parcel Tracking declarations
#If you want to use parcel tracking, register for a free account at: https://www.aftership.com
#Add the API number and uncomment next two lines
#parcelapi = aftership.APIv4('YOUR-AFTERSHIP-API-NUMBER')
#couriers = parcelapi.couriers.all.get()
number = ''
slug=''

#Parcel Tracking
def track():
    text=api.trackings.get(tracking=dict(slug=slug, tracking_number=number))
    numtrack=len(text['trackings'])
    print("Total Number of Parcels: " + str(numtrack))
    if numtrack==0:
        parcelnotify=("You have no parcel to track")
        say(parcelnotify)
    elif numtrack==1:
        parcelnotify=("You have one parcel to track")
        say(parcelnotify)
    elif numtrack>1:
        parcelnotify=( "You have " + str(numtrack) + " parcels to track")
        say(parcelnotify)
    for x in range(0,numtrack):
        numcheck=len(text[ 'trackings'][x]['checkpoints'])
        description = text['trackings'][x]['checkpoints'][numcheck-1]['message']
        parcelid=text['trackings'][x]['tracking_number']
        trackinfo= ("Parcel Number " + str(x+1)+ " with tracking id " + parcelid + " is "+ description)
        say(trackinfo)
        #time.sleep(10)
