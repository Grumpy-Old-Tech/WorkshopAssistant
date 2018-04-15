#!/usr/bin/env python

#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
from ActionsYouTube import youtube_search

import time
import pychromecast

#Chromecast Constants
CHROMECAST_IP = '192.168.1.13'  #Change ip to match the ip-address of your Chromecast


def chromecastPlayVideo(phrase):
    # Chromecast declarations
    # Do not rename/change "TV" its a variable
    TV = pychromecast.Chromecast(CHROMECAST_IP)
    mc = TV.media_controller
    idx=phrase.find('play')
    query=phrase[idx:]
    query=query.replace("'}", "",1)
    query=query.replace('play','',1)
    query=query.replace('on chromecast','',1)
    query=query.strip()
    youtubelinks=youtube_search(query)
    youtubeurl=youtubelinks[0]
    streams=youtube_stream_link(youtubeurl)
    videostream=streams[1]
    TV.wait()
    time.sleep(1)
    mc.play_media(videostream,'video/mp4')

def chromecastControl(phrase):
    # Chromecast declarations
    # Do not rename/change "TV" its a variable
    TV = pychromecast.Chromecast(CHROMECAST_IP)
    mc = TV.media_controller
    if 'pause' in phrase:
        TV.wait()
        time.sleep(1)
        mc.pause()

    if 'resume' in phrase:
        TV.wait()
        time.sleep(1)
        mc.play()

    if 'end' in phrase:
        TV.wait()
        time.sleep(1)
        mc.stop()

    if 'volume' in phrase:
        if 'up' in phrase:
            TV.wait()
            time.sleep(1)
            TV.volume_up(0.2)

        if 'down' in phrase:
            TV.wait()
            time.sleep(1)
            TV.volume_down(0.2)


def chromecastActions(phrase):
    if 'play' in phrase:
        chromecastPlayVideo(phrase)
    else:
        chromecastControl(phrase)
