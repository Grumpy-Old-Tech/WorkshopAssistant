#!/usr/bin/env python

import os
from Talker import say
from Player import setPlayerStartVolume

#Number of station names and station links should be the same
stnname=('Radio Triple m', 'Radio K O', 'Radio N X', 'Radio ABC')#Add more stations if you want
stnlink=('http://stream.scahw.com.au/live/3mmm_128.stream/playlist.m3u8', 'http://stream.scahw.com.au/live/2kko_32.stream/manifest.m3u8', 'http://stream.scahw.com.au/live/2xxx_32.stream/manifest.m3u8', 'http://abc.net.au/res/streaming/audio/aac/local_newcastle.pls')

#Radio Station Streaming
def radio(phrase):
    station = ""
    for num, name in enumerate(stnname):
        if name.lower() in phrase:
            startingvol=setPlayerStartVolume()
            station=stnlink[num]
            break

    if station != "":
        print (station)
        say("Tuning into " + name)
        os.system('mpv --really-quiet --volume='+str(startingvol)+' '+station+' &')
    else:
        say("Sorry, I don't know that radio station")
