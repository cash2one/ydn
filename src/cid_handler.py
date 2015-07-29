#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web

import libs
from keyword_map import KeywordMap

cid_logger = libs.get_logger('cid')


class CategoryHandler(tornado.web.RequestHandler):

    __keyword_map = KeywordMap()

    def __get_cid(self, keyword):
        '''依据输入的关键词返回映射的 Categroy ID.

        参数:
            keyword: 关键词

        返回:
            如果有映射关系, 返回 Category ID, 否则返回 None.
        '''
        return self.__class__.__keyword_map.get(keyword)

    def get(self):
        '''依据请求的关键词返回 Category ID.

        当前版本的关键词使用的是读音, 且不考虑上下文关系.

        参数:
            keyword: 关键词 (发音)

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
        global cid_logger

        # keyword
        keyword = self.get_argument('kw', None)
        session_id = self.get_argument('sid', None)

        errno = 0
        msg = None
        data = None
        if keyword is None or session_id is None:
            errno = 1
            msg = 'invalid params'
            data = msg
        else:
            try:
                cid = self.__get_cid(keyword)
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

        log_string = 'ip={}, kw={}, sid={}, errno={}, msg={}, rt={:.3f}'.format(
            self.request.remote_ip, keyword.encode("utf-8"), session_id, errno,
            msg, 1000.0 * self.request.request_time(),
        )

        cid_logger.info(log_string)
        ret_json = libs.utils.compose_ret(errno, data)
        self.write(ret_json)
