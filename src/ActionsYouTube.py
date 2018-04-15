#!/usr/bin/env python

from Talker import say
from Player import setPlayerStartVolume

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#from gmusicapi import Mobileclient

import requests
import os
import os.path
import time
import re
import subprocess
import json
import urllib.request
import pafy

#API Key for YouTube and KS Search Engine
google_cloud_api_key='AIzaSyAQAN0Y97ZU5m6ETwDmaHePHFgYXuDaegQ'

#YouTube API Constants
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


#Function to search YouTube and get videoid
def youtube_search(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=google_cloud_api_key)

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


#Function to get streaming links for YouTube URLs
def youtube_stream_link(videourl):
    url=videourl
    video = pafy.new(url)
    bestvideo = video.getbest()
    bestaudio = video.getbestaudio()
    audiostreaminglink=bestaudio.url
    videostreaminglink=bestvideo.url
    return audiostreaminglink,videostreaminglink


#----------Getting urls for YouTube autoplay-----------------------------------
def fetchautoplaylist(url,numvideos):
    videourl=url
    autonum=numvideos
    autoplay_urls=[]
    autoplay_urls.append(videourl)
    for i in range(0,autonum):
        response=urllib.request.urlopen(videourl)
        webContent = response.read()
        webContent = webContent.decode('utf-8')
        idx=webContent.find("Up next")
        getid=webContent[idx:]
        idx=getid.find('<a href="/watch?v=')
        getid=getid[idx:]
        getid=getid.replace('<a href="/watch?v=',"",1)
        getid=getid.strip()
        idx=getid.find('"')
        videoid=getid[:idx]
        videourl=('https://www.youtube.com/watch?v='+videoid)
        if not videourl in autoplay_urls:
            i=i+1
            autoplay_urls.append(videourl)
        else:
            i=i-1
            continue
##    print(autoplay_urls)
    return autoplay_urls


#-----------------Start of Functions for YouTube Streaming---------------------
def youtubeplayer():

    if os.path.isfile("/home/pi/.youtubeplayer.json"):
        with open('/home/pi/.youtubeplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.youtubeplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.youtubeplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    if os.path.isfile("/home/pi/youtubeurllist.json"):
        with open('/home/pi/youtubeurllist.json','r') as input_file:
            tracks= json.load(input_file)
            numtracks=len(tracks)
            print(tracks)
    else:
        tracks=""
        numtracks=0

    startingvol = setPlayerStartVolume()

    if not tracks==[]:
        if currenttrackid<numtracks:
            audiostream,videostream=youtube_stream_link(tracks[currenttrackid])
            streamurl=audiostream
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/pi/.youtubeplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            audiostream,videostream=youtube_stream_link(tracks[currenttrackid])
            streamurl=audiostream
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")

def YouTube_Autoplay(phrase):
    urllist=[]
    idx=phrase.find('stream')
    track=phrase[idx:]
    track=track.replace("'}", "",1)
    track = track.replace('stream','',1)
    track=track.strip()
    say("Getting autoplay links")
    fullurl,urlid=youtube_search(track)
    autourls=fetchautoplaylist(fullurl,10)#Maximum of 10 URLS
    print(autourls)
    for i in range(0,len(autourls)):
        urllist.append(autourls[i])
    say("Adding autoplay links to the playlist")
    with open('/home/pi/youtubeurllist.json', 'w') as output_file:
        json.dump(autourls, output_file)
    if os.path.isfile("/home/pi/.youtubeplayer.json"):
        os.remove('/home/pi/.youtubeplayer.json')
    youtubeplayer()


def YouTube_No_Autoplay(phrase):
    urllist=[]
    idx=phrase.find('stream')
    track=phrase[idx:]
    track=track.replace("'}", "",1)
    track = track.replace('stream','',1)
    track=track.strip()
    say("Getting youtube link")
    fullurl,urlid=youtube_search(track)
    urllist.append(fullurl)
    print(urllist)
    with open('/home/pi/youtubeurllist.json', 'w') as output_file:
        json.dump(urllist, output_file)
    if os.path.isfile("/home/pi/.youtubeplayer.json"):
        os.remove('/home/pi/.youtubeplayer.json')
    youtubeplayer()

def streamActions(phase):
    os.system('pkill mpv')
    if os.path.isfile("/home/pi/GassistPi/src/trackchange.py"):
        os.system('rm /home/pi/GassistPi/src/trackchange.py')
        if 'autoplay' in phase:
            os.system('echo "from actions import youtubeplayer\n\n" >> /home/pi/GassistPi/src/trackchange.py')
            os.system('echo "youtubeplayer()\n" >> /home/pi/GassistPi/src/trackchange.py')
            YouTube_Autoplay(str(phase).lower())
        else:
            YouTube_No_Autoplay(phase)
    else:
        if 'autoplay' in phase:
            os.system('echo "from actions import youtubeplayer\n\n" >> /home/pi/GassistPi/src/trackchange.py')
            os.system('echo "youtubeplayer()\n" >> /home/pi/GassistPi/src/trackchange.py')
            YouTube_Autoplay(phase)
        else:
            YouTube_No_Autoplay(phase)

