#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web
import socket

from .. import libs
import define


trace_logger = libs.get_logger('trace')
__all__ = ['TraceHandler']


class TraceHandler(tornado.web.RequestHandler):

    def get(self):
        '''用来追踪用户的行为

        参数:
            user_id: 用户 ID
            event: 统计的事件
            value: 统计事件的值, 可以是计数, 可以是特定值, 依据业务变动
        '''
        global trace_logger

        event_id = self.get_argument('eid', None)
        user_id = self.get_argument('uid', None)
        session_id = self.get_argument('sid', None)
        value = self.get_argument('v', None)
        try:
            event_id = int(event_id)
        except ValueError:
            event_id = define.EVENT_INVALID

        errno = define.ERR_SUCCESS
        log_string = None
        ip = self.request.headers.get('clientip', None)
        if None in (event_id, user_id, value):
            errno = define.EVENT_INVALID_PARAMS
            log_string = 'errno={errno}\tip={ip}\tuid={uid}'.format(
                errno=errno,
                uid=user_id,
                ip=ip,
            )
        else:
            # eid = 0, 1
            # 用户是否展示/点击了广告
            # value 表示 session ID
            if event_id in (define.EVENT_DISPLAY, define.EVENT_CLICK_AD):
                log_string = ('errno={errno}\teid={eid}\tuid={uid}\t'
                              'sid={sid}').format(
                    errno=errno,
                    eid=event_id,
                    uid=user_id,
                    sid=value if sid is None else sid,
                )
            # eid = 2
            # 用户在广告内展示的毫秒数
            elif event_id == define.EVENT_DISPLAY_DURATION:
                log_string = ('errno={errno}\teid={eid}\tuid={uid}\t'
                              'sid={sid}\tvalue={value}').format(
                    errno=errno,
                    eid=event_id,
                    uid=user_id,
                    sid=session_id,
                    value=value,
                )
            else:
                errno = define.ERR_TRACE_INVALID_EVENT
                log_string = 'errno={errno}\tip={ip}\tuid={uid}'.format(
                    errno=errno,
                    uid=user_id,
                    ip=self.request.remote_ip,
                )
            trace_logger.info(log_string)

        ret_json = libs.utils.compose_ret(errno)
        self.write(ret_json)
