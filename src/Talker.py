#!/usr/bin/env python

from googletrans import Translator
from gtts import gTTS
import os
import os.path

##Speech and translator declarations
ttsfilename="/tmp/say.mp3"
translator = Translator()
language='en'
## Other language options:
##'af'    : 'Afrikaans'         'sq' : 'Albanian'           'ar' : 'Arabic'      'hy'    : 'Armenian'
##'bn'    : 'Bengali'           'ca' : 'Catalan'            'zh' : 'Chinese'     'zh-cn' : 'Chinese (China)'
##'zh-tw' : 'Chinese (Taiwan)'  'hr' : 'Croatian'           'cs' : 'Czech'       'da'    : 'Danish'
##'nl'    : 'Dutch'             'en' : 'English'            'eo' : 'Esperanto'   'fi'    : 'Finnish'
##'fr'    : 'French'            'de' : 'German'             'el' : 'Greek'       'hi'    : 'Hindi'
##'hu'    : 'Hungarian'         'is' : 'Icelandic'          'id' : 'Indonesian'  'it'    : 'Italian'
##'ja'    : 'Japanese'          'km' : 'Khmer (Cambodian)'  'ko' : 'Korean'      'la'    : 'Latin'
##'lv'    : 'Latvian'           'mk' : 'Macedonian'         'no' : 'Norwegian'   'pl'    : 'Polish'
##'pt'    : 'Portuguese'        'ro' : 'Romanian'           'ru' : 'Russian'     'sr'    : 'Serbian'
##'si'    : 'Sinhala'           'sk' : 'Slovak'             'es' : 'Spanish'     'sw'    : 'Swahili'
##'sv'    : 'Swedish'           'ta' : 'Tamil'              'th' : 'Thai'        'tr'    : 'Turkish'
##'uk'    : 'Ukrainian'         'vi' : 'Vietnamese'         'cy' : 'Welsh'

#Text to speech converter with translation
def say(words):
    words= translator.translate(words, dest=language)
    words=words.text
    words=words.replace("Text, ",'',1)
    words=words.strip()
    print(words)
    tts = gTTS(text=words, lang=language)
    tts.save(ttsfilename)
    os.system("mpg123 "+ttsfilename)
    os.remove(ttsfilename)
