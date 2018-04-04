#!/usr/bin/env python

from pushbullet import Pushbullet

def pushmessage(title,body):
    pb = Pushbullet('ENTER-YOUR-PUSHBULLET-KEY-HERE')
    push = pb.push_note(title,body)
