#!/usr/bin/env python

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmusicapi import Mobileclient
from googletrans import Translator
from pushbullet import Pushbullet
from gtts import gTTS
import requests
import time
import re
import subprocess
import aftership
import feedparser
import json
import urllib.request
import pafy
import pychromecast
import os
import os.path
from Talker import say
from Player import setPlayerStartVolume


#Google Music Declarations
song_ids=[]
track_ids=[]
api = Mobileclient()
#If you are using two-step authentication, use app specific password. For guidelines, go through README
logged_in = api.login('ENTER_YOUR_EMAIL_HERE', 'ENETER_YOUR_PASSWORD', Mobileclient.FROM_MAC_ADDRESS)


def loadsonglist():
    song_ids=[]
    if os.path.isfile("/home/pi/songs.json"):
        with open('/home/pi/songs.json','r') as input_file:
            songs_list= json.load(input_file)
##            print(songs_list)
    else:
        songs_list= api.get_all_songs()
        with open('/home/pi/songs.json', 'w') as output_file:
            json.dump(songs_list, output_file)
    for i in range(0,len(songs_list)):
        song_ids.append(songs_list[i]['id'])
    songsnum=len(songs_list)
    return song_ids, songsnum

def loadartist(artistname):
    song_ids=[]
    artist=str(artistname)
    if os.path.isfile("/home/pi/songs.json"):
        with open('/home/pi/songs.json','r') as input_file:
            songs_list= json.load(input_file)
##            print(songs_list)
    else:
        songs_list= api.get_all_songs()
        with open('/home/pi/songs.json', 'w') as output_file:
            json.dump(songs_list, output_file)
    for i in range(0,len(songs_list)):
        if artist.lower() in (songs_list[i]['albumArtist']).lower():
            song_ids.append(songs_list[i]['id'])
        else:
            print("Artist not found")
    songsnum=len(song_ids)
    return song_ids, songsnum

def loadalbum(albumname):
    song_ids=[]
    album=str(albumname)
    if os.path.isfile("/home/pi/songs.json"):
        with open('/home/pi/songs.json','r') as input_file:
            songs_list= json.load(input_file)
##            print(songs_list)
    else:
        songs_list= api.get_all_songs()
        with open('/home/pi/songs.json', 'w') as output_file:
            json.dump(songs_list, output_file)
    for i in range(0,len(songs_list)):
        if album.lower() in (songs_list[i]['album']).lower():
            song_ids.append(songs_list[i]['id'])
        else:
            print("Album not found")
    songsnum=len(song_ids)
    return song_ids, songsnum

def loadplaylist(playlistnum):
    track_ids=[]
    if os.path.isfile("/home/pi/playlist.json"):
        with open('/home/pi/playlist.json','r') as input_file:
            playlistcontents= json.load(input_file)
    else:
        playlistcontents=api.get_all_user_playlist_contents()
        with open('/home/pi/playlist.json', 'w') as output_file:
            json.dump(playlistcontents, output_file)
##        print(playlistcontents[0]['tracks'])

    for k in range(0,len(playlistcontents[playlistnum]['tracks'])):
        track_ids.append(playlistcontents[playlistnum]['tracks'][k]['trackId'])
##        print(track_ids)
    tracksnum=len(playlistcontents[playlistnum]['tracks'])
    return track_ids, tracksnum

def refreshlists():
    playlist_list=api.get_all_user_playlist_contents()
    songs_list=api.get_all_songs()
    with open('/home/pi/songs.json', 'w') as output_file:
        json.dump(songs_list, output_file)
    with open('/home/pi/playlist.json', 'w') as output_file:
        json.dump(playlist_list, output_file)
    say("Music list synchronised")

def play_playlist(playlistnum):

    if os.path.isfile("/home/pi/.gmusicplaylistplayer.json"):
        with open('/home/pi/.gmusicplaylistplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicplaylistplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicplaylistplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    tracks,numtracks=loadplaylist(playlistnum)
    startingvol=mpvvolmgr()

    if not tracks==[]:
        if currenttrackid<numtracks:
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/pi/.gmusicplaylistplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")


def play_songs():

    if os.path.isfile("/home/pi/.gmusicsongsplayer.json"):
        with open('/home/pi/.gmusicsongsplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicsongsplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicsongsplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    tracks,numtracks=loadsonglist()
    startingvol=setPlayerStartVolume()

    if not tracks==[]:
        if currenttrackid<numtracks:
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/pi/.gmusicsongsplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")


def play_album(albumname):
    if os.path.isfile("/home/pi/.gmusicalbumplayer.json"):
        with open('/home/pi/.gmusicalbumplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicalbumplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicalbumplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    tracks,numtracks=loadalbum(albumname)
    startingvol=setPlayerStartVolume()

    if not tracks==[]:
        if currenttrackid<numtracks:
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/pi/.gmusicalbumplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")


def play_artist(artistname):
    if os.path.isfile("/home/pi/.gmusicartistplayer.json"):
        with open('/home/pi/.gmusicartistplayer.json','r') as input_file:
            playerinfo= json.load(input_file)
        currenttrackid=playerinfo[0]
        loopstatus=playerinfo[1]
        nexttrackid=currenttrackid+1
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicartistplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)
    else:
        currenttrackid=0
        nexttrackid=1
        loopstatus='on'
        playerinfo=[nexttrackid,loopstatus]
        with open('/home/pi/.gmusicartistplayer.json', 'w') as output_file:
            json.dump(playerinfo, output_file)

    tracks,numtracks=loadartist(artistname)
    startingvol=setPlayerStartVolume()

    if not tracks==[]:
        if currenttrackid<numtracks:
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='on':
            currenttrackid=0
            nexttrackid=1
            loopstatus='on'
            playerinfo=[nexttrackid,loopstatus]
            with open('/home/pi/.gmusicartistplayer.json', 'w') as output_file:
                json.dump(playerinfo,output_file)
            streamurl=api.get_stream_url(tracks[currenttrackid])
            streamurl=("'"+streamurl+"'")
            print(streamurl)
            os.system('mpv --really-quiet --volume='+str(startingvol)+' '+streamurl+' &')
        elif currenttrackid>=numtracks and loopstatus=='off':
            print("Error")
    else:
        say("No matching results found")

def googleMusicSelect(phrase):
    os.system('pkill mpv')
    if os.path.isfile("/home/pi/GassistPi/src/trackchange.py"):
        os.system('rm /home/pi/GassistPi/src/trackchange.py')
    
    os.system('echo "from actions import play_playlist\nfrom actions import play_songs\nfrom actions import play_album\nfrom actions import play_artist\n\n" >> /home/pi/GassistPi/src/trackchange.py')
    if 'all the songs' in phrase:
        os.system('echo "play_songs()\n" >> /home/pi/GassistPi/src/trackchange.py')
        say("Playing all your songs")
        play_songs()

    if 'playlist' in phrase:
        if 'first' in phrase or 'one' in phrase  or '1' in phrase:
            os.system('echo "play_playlist(0)\n" >> /home/pi/GassistPi/src/trackchange.py')
            say("Playing songs from your playlist")
            play_playlist(0)
        else:
            say("Sorry I am unable to help")

    if 'album' in phrase:
        if os.path.isfile("/home/pi/.gmusicalbumplayer.json"):
            os.system("rm /home/pi/.gmusicalbumplayer.json")

        req=phrase
        idx=(req).find('album')
        album=req[idx:]
        album=album.replace("'}", "",1)
        album = album.replace('album','',1)
        if 'from'.lower() in req:
            album = album.replace('from','',1)
            album = album.replace('google music','',1)
        else:
            album = album.replace('google music','',1)

        album=album.strip()
        print(album)
        albumstr=('"'+album+'"')
        f = open('/home/pi/GassistPi/src/trackchange.py', 'a+')
        f.write('play_album('+albumstr+')')
        f.close()
        say("Looking for songs from the album")
        play_album(album)

    if 'artist' in phrase:
        if os.path.isfile("/home/pi/.gmusicartistplayer.json"):
            os.system("rm /home/pi/.gmusicartistplayer.json")

        req=phrase
        idx=(req).find('artist')
        artist=req[idx:]
        artist=artist.replace("'}", "",1)
        artist = artist.replace('artist','',1)
        if 'from'.lower() in req:
            artist = artist.replace('from','',1)
            artist = artist.replace('google music','',1)
        else:
            artist = artist.replace('google music','',1)

        artist=artist.strip()
        print(artist)
        artiststr=('"'+artist+'"')
        f = open('/home/pi/GassistPi/src/trackchange.py', 'a+')
        f.write('play_artist('+artiststr+')')
        f.close()
        say("Looking for songs rendered by the artist")
        play_artist(artist)
