#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web

from .. import libs
from .. import ssp
import define

cid_logger = libs.get_logger('cid')
__all__ = ['CategoryHandler']


class CidHandler(tornado.web.RequestHandler):

    __ad_manager = ssp.AdManager()

    def __get_cid(self, keyword):
        '''依据输入的关键词返回映射的 Categroy ID.

        参数:
            keyword: 关键词

        返回:
            如果有映射关系, 返回 Category ID, 否则返回 None.
        '''
        token = None
        try:
            src, token = self.__class__.__ad_manager.get_src_token(
                keyword, ssp.define.KEY_TYPE_WORD
            )
        except KeyError:
            pass
        else:
            # 只要 YDN 的情况
            if src != ssp.define.SRC_YDN:
                token = None

        return token

    def get(self):
        '''依据请求的关键词返回 Category ID.

        当前版本的关键词使用的是读音, 且不考虑上下文关系.

        参数:
            keyword: 关键词 (发音)
            session_id: Session 号, 用来串数据
            user_id: 用户 ID

        返回:
            返回 JSON, 格式如下:

        {
            'errno': 正整数错误码,
            'data': {'cid': Category ID},
        }
        '''
        global cid_logger

        # keyword
        keyword = self.get_argument('kw', None)
        session_id = self.get_argument('sid', None)
        user_id = self.get_argument('uid', None)

        errno, msg, data = [None] * 3
        if None in (keyword, session_id, user_id):
            errno = define.ERR_INVALID_PARAMS
            msg = define.MSG_INVALID_PARAMS
        else:
            cid = self.__get_cid(keyword)
            if cid is None:
                errno = define.ERR_CID_NO_CATEGORY
                msg = define.MSG_CID_NO_CATEGORY
            else:
                errno = define.ERR_SUCCESS
                msg = cid
                data = {'cid': cid}

        ip = self.request.headers.get('clientip', None)
        log_string = ('ip={ip}\tkw={kw}\tuid={uid}\tsid={sid}\terrno={errno}\t'
                      'msg={msg}\trt={rt:.3f}').format(
            ip=ip,
            kw=keyword.encode("utf-8"),
            uid=user_id,
            sid=session_id,
            errno=errno,
            msg=msg,
            rt=1000.0 * self.request.request_time(),
        )

        cid_logger.info(log_string)
        ret_json = libs.utils.compose_ret(errno, data)
        self.write(ret_json)
