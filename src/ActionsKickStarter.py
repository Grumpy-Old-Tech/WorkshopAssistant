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
from Talker import say

#API Key for YouTube and KS Search Engine
google_cloud_api_key='AIzaSyAQAN0Y97ZU5m6ETwDmaHePHFgYXuDaegQ'

#Function for google KS custom search engine
def kickstrater_search(query):
    service = build("customsearch", "v1",
            developerKey=google_cloud_api_key)
    res = service.cse().list(
        q=query,
        cx = '012926744822728151901:gefufijnci4',
        ).execute()
    return res

#-------------------Start of Kickstarter Search functions-----------------------
def campaign_page_parser(campaignname):
    page_link=kickstrater_search(campaignname)
    kicktrackurl=page_link['items'][0]['link']
    response=urllib.request.urlopen(kicktrackurl)
    webContent = response.read()
    webContent = webContent.decode('utf-8')
    return webContent

def kickstarter_get_data(page_source,parameter):
    idx=page_source.find(parameter)
    info=page_source[idx:]
    info=info.replace(parameter,"",1)
    idx=info.find('"')
    info=info[:idx]
    info=info.replace('"',"",1)
    info=info.strip()
    result=info
    return result

def get_campaign_title(campaign):
    campaigntitle=campaign
    campaigntitleidx1=campaigntitle.find('<title>')
    campaigntitleidx2=campaigntitle.find('&mdash;')
    campaigntitle=campaigntitle[campaigntitleidx1:campaigntitleidx2]
    campaigntitle=campaigntitle.replace('<title>',"",1)
    campaigntitle=campaigntitle.replace('&mdash;',"",1)
    campaigntitle=campaigntitle.strip()
    return campaigntitle

def get_pledges_offered(campaign):
    pledgesoffered=campaign
    pledgenum=0
    for num in re.finditer('pledge__reward-description pledge__reward-description--expanded',pledgesoffered):
        pledgenum=pledgenum+1
    return pledgenum

def get_funding_period(campaign):
    period=campaign
    periodidx=period.find('Funding period')
    period=period[periodidx:]
    periodidx=period.find('</p>')
    period=period[:periodidx]
    startperiodidx1=period.find('class="invisible-if-js js-adjust-time">')
    startperiodidx2=period.find('</time>')
    startperiod=period[startperiodidx1:startperiodidx2]
    startperiod=startperiod.replace('class="invisible-if-js js-adjust-time">','',1)
    startperiod=startperiod.replace('</time>','',1)
    startperiod=startperiod.strip()
    period2=period[startperiodidx2+5:]
    endperiodidx1=period2.find('class="invisible-if-js js-adjust-time">')
    endperiodidx2=period2.find('</time>')
    endperiod=period2[endperiodidx1:endperiodidx2]
    endperiod=endperiod.replace('class="invisible-if-js js-adjust-time">','',1)
    endperiod=endperiod.replace('</time>','',1)
    endperiod=endperiod.strip()
    duration=period2[endperiodidx2:]
    duration=duration.replace('</time>','',1)
    duration=duration.replace('(','',1)
    duration=duration.replace(')','',1)
    duration=duration.replace('days','day',1)
    duration=duration.strip()
    return startperiod,endperiod,duration

def kickstarter_tracker(phrase):
    idx=phrase.find('of')
    campaign_name=phrase[idx:]
    campaign_name=campaign_name.replace("kickstarter campaign", "",1)
    campaign_name = campaign_name.replace('of','',1)
    campaign_name=campaign_name.strip()
    campaign_source=campaign_page_parser(campaign_name)
    campaign_title=get_campaign_title(campaign_source)
    campaign_num_rewards=get_pledges_offered(campaign_source)
    successidx=campaign_source.find('to help bring this project to life.')
    if str(successidx)==str(-1):
        backers=kickstarter_get_data(campaign_source,'data-backers-count="')
        totalpledged=kickstarter_get_data(campaign_source,'data-pledged="')
        totaltimerem=kickstarter_get_data(campaign_source,'data-hours-remaining="')
        totaldur=kickstarter_get_data(campaign_source,'data-duration="')
        endtime=kickstarter_get_data(campaign_source,'data-end_time="')
        goal=kickstarter_get_data(campaign_source,'data-goal="')
        percentraised=kickstarter_get_data(campaign_source,'data-percent-raised="')
        percentraised=round(float(percentraised),2)
        if int(totaltimerem)>0:
            #print(campaign_title+" is an ongoing campaign with "+str(totaltimerem)+" hours of fundraising still left." )
            say(campaign_title+" is an ongoing campaign with "+str(totaltimerem)+" hours of fundraising still left." )
            #print("Till now, "+str(backers)+ " backers have pledged for "+str(campaign_num_rewards)+" diferent rewards raising $"+str(totalpledged)+" , which is "+str(percentraised)+" times the requested amount of $"+str(goal))
            say("Till now, "+str(backers)+ " backers have pledged for "+str(campaign_num_rewards)+" diferent rewards raising $"+str(totalpledged)+" , which is "+str(percentraised)+" times the requested amount of $"+str(goal))
        if float(percentraised)<1 and int(totaltimerem)<=0:
            #print(campaign_title+" has already ended")
            say(campaign_title+" has already ended")
            #print(str(backers)+ " backers raised $"+str(totalpledged)+" , which was "+str(percentraised)+" times the requested amount of $"+str(goal))
            say(str(backers)+ " backers raised $"+str(totalpledged)+" , which was "+str(percentraised)+" times the requested amount of $"+str(goal))
            #print(campaign_title+" was unseccessful in raising the requested amount of $"+str(goal)+" ." )
            say(campaign_title+" was unseccessful in raising the requested amount of $"+str(goal)+" ." )
        if float(percentraised)>1 and int(totaltimerem)<=0:
            #print(campaign_title+" has already ended")
            say(campaign_title+" has already ended")
            #print(str(backers)+ " backers raised $"+str(totalpledged)+" , which was "+str(percentraised)+" times the requested amount of $"+str(goal))
            say(str(backers)+ " backers raised $"+str(totalpledged)+" , which was "+str(percentraised)+" times the requested amount of $"+str(goal))
            #print("Though the funding goal was reached, due to reasons undisclosed, the campaign was either cancelled by the creator or Kickstarter.")
            say("Though the funding goal was reached, due to reasons undisclosed, the campaign was either cancelled by the creator or Kickstarter.")
    else:
        [start_day,end_day,numdays]=get_funding_period(campaign_source)
        campaigninfo=campaign_source[(successidx-100):(successidx+35)]
        campaignidx=campaigninfo.find('<b>')
        campaigninfo=campaigninfo[campaignidx:]
        campaigninfo=campaigninfo.replace('<b>',"",1)
        campaigninfo=campaigninfo.replace('</b>',"",1)
        campaigninfo=campaigninfo.replace('<span class="money">',"",1)
        campaigninfo=campaigninfo.replace('</span>',"",1)
        campaigninfo=campaigninfo.strip()
        #print(campaign_title+" was a "+str(numdays)+" campaign launched on "+str(start_day))
        #print(campaigninfo)
        say(campaign_title+" was a "+str(numdays)+" campaign launched on "+str(start_day))
        say(campaigninfo)
