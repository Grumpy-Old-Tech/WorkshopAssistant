#!/usr/bin/env python

import time

import RPi.GPIO as GPIO
from Talker import say

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Number of entities in 'var' and 'PINS' should be the same
gpioDevices = ('kitchen lights', 'bathroom lights', 'bedroom lights') #Add whatever names you want. This is case is insensitive
gpioPins = (12,13,24) #GPIOS for 'devices'. Add other GPIOs that you want

for pin in gpioPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

#Indicator Pins
GPIO.setup(25, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
led=GPIO.PWM(25,1)
led.start(0)

#Stopbutton
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def conversationStarted():
    GPIO.output(5,GPIO.HIGH)
    GPIO.output(6,GPIO.LOW)
    led.ChangeDutyCycle(100)

def responseStarted():
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.HIGH)
    led.ChangeDutyCycle(50)

def responseFinished():
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.HIGH)
    led.ChangeDutyCycle(100)

def conversationFinished():
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.LOW)
    led.ChangeDutyCycle(0)

def gpio(phrase):
    if 'servo' in phrase:
        for s in re.findall(r'\b\d+\b', phrase):
            setAngle(int(s))
    else:
        for num, name in enumerate(gpioDevices):
            if name.lower() in phrase:
                pinout=gpioPins[num]
                if 'on' in phrase:
                    GPIO.output(pinout, 1)
                    say("OK Turning On " + name)
                elif 'off' in phrase:
                    GPIO.output(pinout, 0)
                    say("OK Turning Off " + name)
