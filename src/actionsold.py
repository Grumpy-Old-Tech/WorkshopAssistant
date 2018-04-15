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
import RPi.GPIO as GPIO
import time
import re
import subprocess
import json
import urllib.request
import pafy

#API Key for YouTube and KS Search Engine
google_cloud_api_key='ENTER-YOUR-GOOGLE-CLOUD-API-KEY-HERE'

#YouTube API Constants
DEVELOPER_KEY = google_cloud_api_key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

playshell = None




