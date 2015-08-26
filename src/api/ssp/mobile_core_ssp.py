#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
try:
    import ujson as json
except:
    import json
import config
import base_ssp
import define
import redis
import msgpack
import sys


class MobileCoreSSP(base_ssp.BaseSSP):

    conf = config.get_config()
    HOST = conf.get('mobile_core', 'host')
    SITEID = conf.get('mobile_core', 'siteid')
    TOKEN = conf.get('mobile_core', 'token')
    COUNTRY = conf.get('mobile_core', 'country')
    PACKAGE_NAME = conf.get('mobile_core', 'package_name')

    # 初始化词典
    host = conf.get('redis', 'host')
    port = conf.getint('redis', 'port')
    db_index = conf.getint('redis', 'db_index')
    dict = redis.StrictRedis(host=host, port=port, db=db_index)

    def __init__(self, token, os, ip, ua):
        base_ssp.BaseSSP.__init__(self, token, os, ip, ua)
        conf = config.get_config()
        self.__prefix = conf.get('mobile_core', 'prefix')

    def __request(self):
        params = {
            'siteid': self.__class__.SITEID,
            'token': self.__class__.TOKEN,
            'country': self.__class__.COUNTRY,
            'packageName': self.__class__.PACKAGE_NAME,
        }
        if self.os == define.OS_IOS:
            params['platform'] = 'iOS'
        elif self.os == define.OS_ANDROID:
            params['platform'] = 'Android'

        ret = requests.get(self.__class__.HOST, params=params)
        if ret.status_code == requests.codes.ok:
            return ret.text
        else:
            return None

    def __parse(self, text, ostream):
        js = json.loads(text)
        if not js['error']:
            for ad in js['ads']:
                i_url = ad['impressionURL']
                c_url = ad['clickURL']
                title = ad['title']
                creatives = ad['creatives']
                description = ad['description']
                icon = None
                for item in creatives:
                    if item['type'] == 'icon':
                        icon = item['url']

                print >> ostream, ("\t".join([
                    title,
                    description,
                    icon,
                    i_url,
                    c_url,
                ])).encode("utf-8")

    def update(self, ostream=sys.stdout):
        text = self.__request()
        if text is None:
            return
        self.__parse(text, ostream)

    def get(self, key):
        key = self.__prefix + key
        value = self.__class__.dict.get(key)
        if value is not None:
            value = msgpack.unpackb(value)
        return value

    def set(self, key, value):
        if value is None:
            return None

        key = self.__prefix + key
        value = msgpack.packb(value, use_bin_type=True)
        return self.__class__.dict.set(key, value)

    def run(self):
        ret = self.get(self.token)
        if ret is None:
            return False

        self.ad = ret
        return True
