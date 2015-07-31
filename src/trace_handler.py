#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web
import socket

import libs
import ydn


trace_logger = libs.get_logger('trace')

EVENT_CLICK_AD = "1"


class TraceHandler(tornado.web.RequestHandler):

    def get(self):
        '''用来追踪用户的行为

        参数:
            user_id: 用户 ID
            event: 统计的事件
            value: 统计事件的值, 可以是计数, 可以是特定值, 依据业务变动

        错误码包括:
            0   正常返回
            1   请求参数非法
            2   非法事件
        '''
        global trace_logger

        event_id = self.get_argument('eid', None)
        user_id = self.get_argument('uid', None)
        value = self.get_argument('v', None)

        errno = 0
        log_string = None
        if None in (event_id, user_id, value):
            errno = 1
            log_string = 'errno={errno}, ip={ip}, uid={uid}'.format(
                errno=errno,
                uid=user_id,
                ip=self.request.remote_ip,
            )
        else:
            # 用户是否点击了广告
            # value 表示 session ID
            if EVENT_CLICK_AD == event_id:
                log_string = 'errno={errno}, eid={eid}, uid={uid}, sid={sid}'.format(
                    errno=errno,
                    eid=event_id,
                    uid=user_id,
                    sid=value,
                )
            else:
                errno = 2
                log_string = 'errno={errno}, ip={ip}, uid={uid}'.format(
                    errno=errno,
                    uid=user_id,
                    ip=self.request.remote_ip,
                )
            trace_logger.info(log_string)

        ret_json = libs.utils.compose_ret(errno)
        self.write(ret_json)
