#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import tornado.web

from .. import libs
from .. import ssp
import define

logger = libs.get_logger('predict')
__all__ = ['PredictHandler']


class PredictHandler(tornado.web.RequestHandler):

    __ad_manager = ssp.AdManager()

    def __get_ad(self, pron, os, ip, ua):
        ads = self.__class__.__ad_manager.get_ad(
            pron, ssp.define.KEY_TYPE_PRON, os, ip, ua,
        )
        return ads

    def get(self):
        global logger

        pron = self.get_argument('pron', None)
        session_id = self.get_argument('sid', None)
        user_id = self.get_argument('uid', None)
        # Android: 1, iOS: 2
        # 默认为 Android
        os = self.get_argument('os', '1')
        try:
            os = int(os)
        except ValueError:
            os = define.OS_ANDROID

        errno, msg, data = [None] * 3
        ip = self.request.headers.get('clientip', None)
        ua = self.request.headers.get('User-Agent', None)
        if None in (pron, session_id, user_id):
            errno = define.ERR_INVALID_PARAMS
            msg = define.MSG_INVALID_PARAMS
        else:
            data = self.__get_ad(pron, os, ip, ua)
            if data is None:
                errno = define.ERR_PRED_NO_AD
                msg = define.MSG_PRED_NO_AD
            else:
                errno = define.ERR_SUCCESS
                msg = define.MSG_SUCCESS

        log_string = ('ip={ip}\tpron={pron}\tuid={uid}\tsid={sid}\t'
                       'errno={errno}\tmsg={msg}\trt={rt:.3f}').format(
            ip=ip,
            pron=pron,
            uid=user_id,
            sid=session_id,
            errno=errno,
            msg=msg,
            rt=1000.0 * self.request.request_time(),
        )

        logger.info(log_string)
        ret_json = libs.utils.compose_ret(errno, data)
        self.write(ret_json)

