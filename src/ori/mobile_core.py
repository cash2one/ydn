#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
https://www.mobilecore.com/
'''
import requests
import json


class MobileCore(object):

    URL = 'http://api.apprevolve.com/v2/getAds'

    def stream(self):
        params = {
            'siteid': 27361,
            'token': '395aefb13fe001630ac10c75cb6af3cd',
            'platform': 'Android',
            'country': 'JP',
        }
        ret = requests.get(self.__class__.URL, params=params)
        if ret.status_code == 200:
            return ret.text
        else:
            raise ValueError('mobile core has no return')

    def parse(self, text):
        js = json.loads(text)
        if not js['error']:
            for ad in js['ads']:
                i_url = ad['impressionURL']
                c_url = ad['clickURL']
                title = ad['title']
                creatives = ad['creatives']
                category = ad['category']
                description = ad['description']
                icon = None
                for item in creatives:
                    if item['type'] == 'icon':
                        icon = item['url']
                print ("\t".join([
                    category,
                    title,
                    description,
                    icon,
                    i_url,
                    c_url,
                ])).encode("utf-8")


if __name__ == '__main__':
    mobile_core = MobileCore()
    text = mobile_core.stream()
    mobile_core.parse(text)
