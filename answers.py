# -*- coding: utf-8 -*-
import json
import apiai
import smtplib
import pandas as pd
import phonenumbers

from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from langdetect import detect
from googletrans import Translator
from geopy.distance import vincenty
from geopy.geocoders import Nominatim
from validate_email import validate_email


def mobile_validation(number):
    try:
        return carrier._is_mobile(number_type(phonenumbers.parse(number)))
    except Exception:
        return False


def send_email(sender, email):
    bot = 'centrepointbot@gmail.com'
    user = email
    support1 = 'shalini.sharma@landmarkgroup.com'

    password = 'qwerty678606'

    msg1 = '\r\n'.join([
        'From: {}'.format(bot),
        'To: {}'.format(support1),
        'Subject: Centrepoint Bot Report',
        '',
        'Facebook: User {}({}) have some questions. Please, address the same at the earliest.'.format(sender, user)
    ])

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.login(bot, password)
    server.sendmail(bot, [support1], msg1)
    server.quit()


def validate_location(location):
    return geolocator.geocode(location)


def find_near(location):
    lat, long = location.latitude, location.longitude

    temp = ['Country', 'City', 'Street', 'Lat', 'Long', 'Time', 1000000]

    for i in data:
        distance = vincenty((lat, long), (i[3], i[4])).kilometers
        i.append(distance)

        if float(temp[6]) > distance:
            temp = i
        else:
            pass

    return temp


def answer(text):
    request = ai.text_request()
    request.lang, request.query = 'en', text

    result = json.loads(request.getresponse().read()).get('result').get('fulfillment').get('messages')[0].get('speech')

    return result


def get_answer(sender, message):
    try:
        language = detect(message)
    except Exception:
        language = 'en'


    if language == 'ar':
        try:
            message = translator.translate(message, dest='en', src='ar').text
        except Exception:
            pass


    try:
        # email = validate_email(message)
        # location = validate_location(message)
        email = None
        location = None
        phone = mobile_validation(message)
    except Exception:
        email = False
        location = None
        phone = mobile_validation(message)

    if phone == True:
        send_email(sender, message)
        result = 'Thank you. Our support will contact to you soon.'
    elif location != None and message.title() and len(message) > 10:
        data = find_near(location)
        result = 'The nearest Centrepoint is in {} only at {} kilometers from you. {}'.format(data[2], round(data[6], 2), data[5])
    else:
        try:
            result = answer(message)
        except Exception:
            result = 'Ooops. Something goes wrong. Please, try again.'

    if language == 'ar':
        result = translator.translate(result, dest='ar', src='en').text

    return result


geolocator = Nominatim()
translator = Translator()
hello = ['Hello', 'Good Day', 'Hi', 'Greetings']
ai = apiai.ApiAI('ab9b502a79c345f9b51f1a83dbdcc053')
data = pd.read_excel('./data/location.xlsx').as_matrix().tolist()

# print(get_answer(u'Hello'))