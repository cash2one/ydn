#!/usr/bin/env python
# -*- encoding: utf-8 -*-


class BaseSSP(object):

    def __init__(self, token, os, ip, ua):
        self.token = token
        self.os = os
        self.ip = ip
        self.ua = ua
        print token, os, ip, ua
        # 用于返回数据
        self.ad = {
            'url': None,
            'description': None,
            'title': None,
            'rank': None,
            'sitehost': None,
            'imp_url': None,
            'icon': None,
        }
        self.feedback = None

    def __compose_ret(self):
        ad_data = []
        ad_data.append(self.ad)
        return {'ads': ad_data, 'feedback': self.feedback}

    def run(self):
        pass

    def get_ad(self):
        if self.run():
            return self.__compose_ret()
        else:
            return None
