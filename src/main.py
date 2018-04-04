#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kodijson import Kodi, PLAYER_VIDEO
import RPi.GPIO as GPIO
import argparse
import os.path
import os
import json
import subprocess
import re
import psutil
import logging
import google.auth.transport.requests
import google.oauth2.credentials
import requests

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
DEVICE_API_URL = 'https://embeddedassistant.googleapis.com/v1alpha2'


from Talker import say
from Player import isPlayerPlaying
from Player import stopPlayer
from Player import pausePlayer
from Player import resumePlayer
from Player import controlPlayerVolume
from ActionsGPIO import gpio
from ActionsExecute import executeScript
from ActionsKickStarter import kickstarter_tracker
from ActionsRadio import radio
from ActionsGoogleMusic import googleMusicSelect
from ActionsGoogleMusic import refreshlists
from ActionsKodi import kodiactions
from ActionsKodi import mutevolstatus
from ActionsNewsFeed import feed
from ActionsParcelTracking import track
from ActionsRecipe import getrecipe
from ActionsESP import ESP
from ActionsHue import hueCheck
from ActionsHue import hueControl
from ActionsTasmota import tasmotaCheck
from ActionsTasmota import tasmotaControl
from ActionsChromecast import chromecastActions
from ActionsYouTube import streamActions

#API Key for YouTube and KS Search Engine
google_cloud_api_key='ENTER-YOUR-GOOGLE-CLOUD-API-KEY-HERE'

logging.basicConfig(filename='/tmp/GassistPi.log', level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Indicator Pins
GPIO.setup(25, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
led=GPIO.PWM(25,1)
led.start(0)

#Buttons
#Stopbutton
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def process_device_actions(event, device_id):
    if 'inputs' in event.args:
        for i in event.args['inputs']:
            if i['intent'] == 'action.devices.EXECUTE':
                for c in i['payload']['commands']:
                    for device in c['devices']:
                        if device['id'] == device_id:
                            if 'execution' in c:
                                for e in c['execution']:
                                    if 'params' in e:
                                        yield e['command'], e['params']
                                    else:
                                        yield e['command'], None


def process_event(event, device_id):
    """Pretty prints events.
    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.
    Args:
        event(event.Event): The current event to process.
    """
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        subprocess.Popen(["aplay", "/home/pi/GassistPi/sample-audio-files/Fb.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #Uncomment the following after starting the Kodi
        #status=mutevolstatus()
        #vollevel=status[1]
        #with open('/home/pi/.volume.json', 'w') as f:
               #json.dump(vollevel, f)
        #kodi.Application.SetVolume({"volume": 0})
        GPIO.output(5,GPIO.HIGH)
        led.ChangeDutyCycle(100)
        print()
        if isPlayerPlaying():
            if os.path.isfile("/home/pi/.mediavolume.json"):
                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume","10"]})+"' | socat - /tmp/mpvsocket")
            else:
                mpvgetvol=subprocess.Popen([("echo '"+json.dumps({ "command": ["get_property", "volume"]})+"' | socat - /tmp/mpvsocket")],shell=True, stdout=subprocess.PIPE)
                output=mpvgetvol.communicate()[0]
                for currntvol in re.findall(r"[-+]?\d*\.\d+|\d+", str(output)):
                    with open('/home/pi/.mediavolume.json', 'w') as vol:
                        json.dump(currntvol, vol)
                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume","10"]})+"' | socat - /tmp/mpvsocket")


    if event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT:
      GPIO.output(5,GPIO.LOW)
      GPIO.output(6,GPIO.LOW)
      led.ChangeDutyCycle(0)
        #Uncomment the following after starting the Kodi
        #with open('/home/pi/.volume.json', 'r') as f:
               #vollevel = json.load(f)
               #kodi.Application.SetVolume({"volume": vollevel})
      if isPlayerPlaying():
          if os.path.isfile("/home/pi/.mediavolume.json"):
              with open('/home/pi/.mediavolume.json', 'r') as vol:
                  oldvollevel = json.load(vol)
              print(oldvollevel)
              mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(oldvollevel)]})+"' | socat - /tmp/mpvsocket")


    if (event.type == EventType.ON_RESPONDING_STARTED and event.args and not event.args['is_error_response']):
       GPIO.output(5,GPIO.LOW)
       GPIO.output(6,GPIO.HIGH)
       led.ChangeDutyCycle(50)

    if event.type == EventType.ON_RESPONDING_FINISHED:
       GPIO.output(6,GPIO.LOW)
       GPIO.output(5,GPIO.HIGH)
       led.ChangeDutyCycle(100)

    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
       GPIO.output (5, GPIO.LOW)
       GPIO.output (6, GPIO.LOW)
       led.ChangeDutyCycle (0)

    print(event)

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        GPIO.output(5,GPIO.LOW)
        GPIO.output(6,GPIO.LOW)
        led.ChangeDutyCycle(0)
        #Uncomment the following after starting the Kodi
        #with open('/home/pi/.volume.json', 'r') as f:
               #vollevel = json.load(f)
               #kodi.Application.SetVolume({"volume": vollevel})
        if isPlayerPlaying():
            if os.path.isfile("/home/pi/.mediavolume.json"):
                with open('/home/pi/.mediavolume.json', 'r') as vol:
                    oldvollevel = json.load(vol)
                print(oldvollevel)
                mpvsetvol=os.system("echo '"+json.dumps({ "command": ["set_property", "volume",str(oldvollevel)]})+"' | socat - /tmp/mpvsocket")

        print()

    if event.type == EventType.ON_DEVICE_ACTION:
        for command, params in process_device_actions(event, device_id):
            print('Do command', command, 'with params', str(params))


def register_device(project_id, credentials, device_model_id, device_id):
    """Register the device if needed.
    Registers a new assistant device if an instance with the given id
    does not already exists for this model.
    Args:
       project_id(str): The project ID used to register device instance.
       credentials(google.oauth2.credentials.Credentials): The Google
                OAuth2 credentials of the user to associate the device
                instance with.
       device_model_id: The registered device model ID.
       device_id: The device ID of the new instance.
    """
    base_url = '/'.join([DEVICE_API_URL, 'projects', project_id, 'devices'])
    device_url = '/'.join([base_url, device_id])
    session = google.auth.transport.requests.AuthorizedSession(credentials)
    r = session.get(device_url)
    print(device_url, r.status_code)
    if r.status_code == 404:
        print('Registering....')
        r = session.post(base_url, data=json.dumps({
            'id': device_id,
            'model_id': device_model_id,
            'client_type': 'SDK_LIBRARY'
        }))
        if r.status_code != 200:
            raise Exception('failed to register device: ' + r.text)
        print('\rDevice registered.')


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    parser.add_argument('--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=True,
                        help='The device model ID registered with Google.')
    parser.add_argument(
        '--project_id',
        type=str,
        metavar='PROJECT_ID',
        required=False,
        help='The project ID used to register device instances.')
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' +
        Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
    with Assistant(credentials, args.device_model_id) as assistant:
        #subprocess.Popen(["aplay", "/home/pi/GassistPi/sample-audio-files/Startup.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        say("Hello I'm your assistant and I'm here to help")
        events = assistant.start()
        print('device_model_id:', args.device_model_id + '\n' + 'device_id:', assistant.device_id + '\n')
        if args.project_id:
            register_device(args.project_id, credentials, args.device_model_id, assistant.device_id)
        for event in events:
            process_event(event, assistant.device_id)
            usrcmd = event.args
            usrCommand = str(usrcmd).lower()

            hueIndex = hueCheck(usrCommand)						#Hue
            if hueIndex > 0:
                assistant.stop_conversation()
                hueControl(usrCommand,hueIndex)
            tasmotaIndex = tasmotaCheck(usrCommand)					#Tasmota
            if tasmotaIndex > -1:
                assistant.stop_conversation()
                tasmotaControl(usrCommand,tasmotaIndex)

            if 'magic mirror' in usrCommand:						#Magic mirror
                assistant.stop_conversation()
                magicMirror(usrCommand)

            if 'ingredients' in usrCommand:						#Ingredients
                assistant.stop_conversation()
                getrecipe(usrCommand)

            if 'kickstarter' in usrCommand:						#Kickstarter
                assistant.stop_conversation()
                kickstarter_tracker(usrCommand)

            if 'turn the' in usrCommand:						#Turn the
                assistant.stop_conversation()
                gpio(usrCommand)

            if 'execute'in usrCommand:							#Execute
                assistant.stop_conversation()
                executeScript(usrCommand)

            if 'stream' in usrCommand:							#Stream
                assistant.stop_conversation()
                stream(usrCommand)
                
            if 'stop' in usrCommand:							#Stop
                stopPlayer()

            if 'radio' in usrCommand:							#Radio
                assistant.stop_conversation()
                radio(usrCommand)

            if 'wireless'in usrCommand:							#Wireless
                assistant.stop_conversation()
                ESP(usrCommand)

            if 'parcel' in usrCommand:							#Parcel
                assistant.stop_conversation()
                track()

            if 'news' in usrCommand:							#News
                assistant.stop_conversation()
                feed(usrCommand)

            if 'feed' in usrCommand:							#Feed
                assistant.stop_conversation()
                feed(usrCommand)
            
            if 'quote' in usrCommand:							#Quote
                assistant.stop_conversation()
                feed(usrCommand)
            
            if 'on kodi' in usrCommand:							#Kodi
                assistant.stop_conversation()
                kodiactions(usrCommand)

            if 'chromecast' in usrCommand:						#Chromecast
                assistant.stop_conversation()
                chromecastActions(usrCommand)

            if 'pause music' in usrCommand:						#Pause music
                assistant.stop_conversation()
                pausePlayer(usrCommand)

            if 'resume music' in usrCommand:						#Resume music
                assistant.stop_conversation()
                resumePlayer(usrCommand)

            if 'music volume' in usrCommand:						#Music volume
                assistant.stop_conversation()
                controlPlayerVolume(usrCommand)
 
            if 'refresh' in usrCommand and 'music' in usrCommand:			#Refresh (Google music)
                assistant.stop_conversation()
                refreshlists()

            if 'google music' in usrCommand:						#Google Music
                assistant.stop_conversation()
                googleMusicSelect(usrCommand)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        logger.exception(error)