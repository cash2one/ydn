#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
value struct is:
{
    's': SOURCE_ID,
    'd': DATA,
}

where, SOURCE_ID as blow:
    0   YDN 意味着只是个 categoryID
    1   mobile core, 是直接使用的广告
'''
import config
import define
import msgpack
import redis
import ydn_ssp
import mobile_core_ssp


class AdManager(object):

    def __init__(self):
        self.__dict = None
        conf = config.get_config()
        self.__prefix = conf.get('ad_manager', 'prefix')
        self.__init_dict()

    def __init_dict(self):
        conf = config.get_config()
        host = conf.get('redis', 'host')
        port = conf.getint('redis', 'port')
        db_index = conf.getint('redis', 'db_index')
        self.__dict = redis.StrictRedis(host=host, port=port, db=db_index)

    def __compose_key(self, key, key_type):
        return "{}_{}_{}".format(
            self.__prefix, key, key_type
        )

    def get(self, key, key_type):
        key = self.__compose_key(key, key_type)
        value = self.__dict.get(key)
        if value is not None:
            value = msgpack.unpackb(value)
        return value

    def set(self, key, key_type, value):
        if value is None:
            return None

        key = self.__compose_key(key, key_type)
        value = msgpack.packb(value, use_bin_type=True)
        return self.__dict.set(key, value)

    def get_ad(self, key, key_type, os, ip, ua):
        ad = self.get(key, key_type)
        src = ad['src']
        token = ad['token']
        ssp = None
        if src == define.SRC_YDN:
            ssp = ydn_ssp.YdnSSP(token, os, ip, ua)
        elif src == define.SRC_MOBILE_CORE:
            ssp = mobile_core_ssp.MobileCoreSSP(token, os, ip, ua)
        else:
            return None

        return ssp.get_ad()


if __name__ == '__main__':
    manager = AdManager()
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'
    print manager.get_ad('trpg', 0, define.OS_ANDROID, '182.22.71.250', ua)
    print manager.get_ad('tadv', 1, define.OS_ANDROID, '182.22.71.250', ua)
    print manager.get_ad('test', 0, define.OS_IOS, '182.22.71.250', ua)
    print manager.get_ad('test', 1, define.OS_ANDROID, '182.22.71.250', ua)
