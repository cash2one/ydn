#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import tornado.web

import libs
from keyword_map import KeywordMap

logger = libs.get_logger('ad')


class PredictHander(tornado.web.RequestHandler):

    __keyword_map = KeywordMap()
    self.__keyword_map.predict()

    def __complete(self, key_word):
        return None

    def __get_ad(self, key_word):
        return None

    def get(self):
        '''依据用户的输入预测出广告

        参数:
            keyword: 关键词发音 (片段)
            session_id: Session 号, 用来串数据
            user_id: 用户 ID

        返回:
            返回 JSON, 格式如下:

        {
            'errno': 正整数错误码,
            'data': {'cid': Category ID},
        }

        其中, 错误码包括:
            0   正常返回
            1   非法请求
            2   内部错误
        '''
        global logger

        # keyword
        keyword = self.get_argument('kw', None)
        session_id = self.get_argument('sid', None)
        user_id = self.get_argument('uid', None)

        errno = 0
        msg = None
        data = None
        if None in (keyword, session_id, user_id):
            errno = 1
            msg = 'invalid params'
            data = msg
        else:
            try:
                cid = self.__get_ad(keyword)
            except Exception as e:
                errno = 2
                msg = str(e)
            else:
                if cid is None:
                    errno = 2
                    msg = 'no category'
                    data = msg
                else:
                    errno = 0
                    msg = cid
                    data = {'cid': cid}


