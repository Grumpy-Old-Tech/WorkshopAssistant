#!/usr/bin/env python

import time
import os
import RPi.GPIO as GPIO
from Talker import say

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Number of entities in 'var' and 'PINS' should be the same
gpioDevices = ('kitchen lights', 'bathroom lights', 'bedroom lights') #Add whatever names you want. This is case is insensitive
gpioPins = (12,13,24) #GPIOS for 'var'. Add other GPIOs that you want

for pin in gpioPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

#Servo pin declaration
GPIO.setup(27, GPIO.OUT)
pwm=GPIO.PWM(27, 50)
pwm.start(0)


#Stepper Motor control
def setAngle(angle):
    duty = angle/18 + 2
    GPIO.output(27, True)
    say("Moving motor by " + str(angle) + " degrees")
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)
    GPIO.output(27, False)


def gpio(phrase):
    if 'servo' in phrase:
        for s in re.findall(r'\b\d+\b', phrase):
            setAngle(int(s))
    if 'zero' in phrase:
        SetAngle(0)
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
