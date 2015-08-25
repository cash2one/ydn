#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
try:
    import lxml.etree as et
except:
    import xml.etree.ElementTree as et
import config
import base_ssp
import define


class YdnSSP(base_ssp.BaseSSP):

    conf = config.get_config()
    HOST = conf.get('ydn', 'host')
    APP_URL = conf.get('ydn', 'app_url')
    ENCODE = conf.get('ydn', 'encode')
    IOS_APPEND = conf.get('ydn', 'ios_append')
    IOS_SOURCE_TOKEN = conf.get('ydn', 'ios_source_token')
    ANDROID_APPEND = conf.get('ydn', 'android_append')
    ANDROID_SOURCE_TOKEN = conf.get('ydn', 'android_source_token')

    def __request(self):
        source_token, append = [None] * 2
        if self.os == define.OS_IOS:
            append = self.__class__.IOS_APPEND
            source_token = self.__class__.IOS_SOURCE_TOKEN
        elif self.os == define.OS_ANDROID:
            append = self.__class__.ANDROID_APPEND
            source_token = self.__class__.ANDROID_SOURCE_TOKEN

        affilData = 'ip={}&ua={} {}'.format(self.ip, self.ua, append)

        params = {
            'maxCount': 1,
            'ctxtUrl': self.__class__.APP_URL,
            'outputCharEnc': self.__class__.ENCODE,
            'affilData': affilData,
            'source': source_token,
            'ctxtId': self.token,
        }
        response = requests.get(self.__class__.HOST, params=params)
        if response.status_code != requests.codes.ok:
            return False
        else:
            self.__parse(response.text.encode("utf-8"))
            return True

    def __parse(self, text):
        root = et.fromstring(text)
        listing = root[1][0]
        self.ad['url'] = listing[0].text
        self.ad['desc'] = listing.attrib.get('description', None)
        self.ad['title'] = listing.attrib.get('title', None)
        self.ad['rank'] = listing.attrib.get('rank', None)
        self.ad['sitehost'] = listing.attrib.get('siteHost', None)
        self.feedback = root[1][-1][0].text

    def run(self):
        return self.__request()
