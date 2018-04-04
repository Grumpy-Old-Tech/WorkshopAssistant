#!/usr/bin/env python

#This is different from AIY Kit's actions
#Copying and Pasting AIY Kit's actions commands will not work


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmusicapi import Mobileclient
from googletrans import Translator
from gtts import gTTS
import requests
import os
import os.path

import time
import re
import subprocess
import json
import urllib.request
import pafy
import pychromecast

#API Key for YouTube and KS Search Engine
google_cloud_api_key='ENTER-YOUR-GOOGLE-CLOUD-API-KEY-HERE'

#YouTube API Constants
DEVELOPER_KEY = google_cloud_api_key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

playshell = None


#Function to search YouTube and get videoid
def youtube_search(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  req=query
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part='id,snippet'
  ).execute()

  videos = []
  channels = []
  playlists = []
  videoids = []
  channelids = []
  playlistids = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.

  for search_result in search_response.get('items', []):

    if search_result['id']['kind'] == 'youtube#video':
      videos.append('%s (%s)' % (search_result['snippet']['title'],
                                 search_result['id']['videoId']))
      videoids.append(search_result['id']['videoId'])

    elif search_result['id']['kind'] == 'youtube#channel':
      channels.append('%s (%s)' % (search_result['snippet']['title'],
                                   search_result['id']['channelId']))
      channelids.append(search_result['id']['channelId'])

    elif search_result['id']['kind'] == 'youtube#playlist':
      playlists.append('%s (%s)' % (search_result['snippet']['title'],
                                    search_result['id']['playlistId']))
      playlistids.append(search_result['id']['playlistId'])

  #Results of YouTube search. If you wish to see the results, uncomment them
  # print 'Videos:\n', '\n'.join(videos), '\n'
  # print 'Channels:\n', '\n'.join(channels), '\n'
  # print 'Playlists:\n', '\n'.join(playlists), '\n'

  #Checks if your query is for a channel, playlist or a video and changes the URL accordingly
  if 'channel'.lower() in  str(req).lower() and len(channels)!=0:
      urlid=channelids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+channelids[0])
  elif 'playlist'.lower() in  str(req).lower() and len(playlists)!=0:
      urlid=playlistids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+playlistids[0])
  else:
      urlid=videoids[0]
      YouTubeURL=("https://www.youtube.com/watch?v="+videoids[0])

  return YouTubeURL,urlid

def chromecastPlayVideo(phrase):
    # Chromecast declarations
    # Do not rename/change "TV" its a variable
    TV = pychromecast.Chromecast("192.168.1.13") #Change ip to match the ip-address of your Chromecast
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
    TV = pychromecast.Chromecast("192.168.1.13") #Change ip to match the ip-address of your Chromecast
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
