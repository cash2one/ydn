#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web
import socket

import libs
import ydn


ad_logger = libs.get_logger('ad')


class ADHandler(tornado.web.RequestHandler):
    '''处理 AD 请求的 Handler.

    请求流程:
        用户请求 Simeji Server (也就是这个代码), 然后 Simeji Server 会请求 Yahoo
        Server, 然后 Yahoo Server 将结果返还给 Simeji Server, 再通过 Simeji
        Server 返回给用户.

        输入为: Yahoo 提供的 Category ID, Category ID 可以通过 CategoryHandler
        来获取.

    优势:
        整个过程中, Yahoo Server 对用户是透明的. 而且与客户端的交互 API
        也是我们自己设定, 所以我们会有更强的掌控能力. 甚至某天我们更换广告提供方
        (Yahoo Server), 对用户而言也是没有区别的.

    返回:
        返回 JSON 格式的数据, 格式为:
        {
            'errno': 正整数错误码,
            'data': [
                {
                    'rank': 排名,
                    'title': 标题,
                    'description': 描述,
                    'url': 广告链接,
                },
                { ... },
                { ... },
                ...,
                    ],
        }

        其中, 错误码包括:
            0   正常返回
            1   非法请求
            2   内部错误
            3   YDN 返回结果非法
            4   qps 禁止
            5   用户达到每日上限
            6   达到用户流量控制上限
    '''

    config = libs.get_config()
    __max_limit = config.getint('ad_server', 'max_limit')
    __default_limit = config.getint('ad_server', 'default_limit')
    __limit_timeout = config.getint('ad_server', 'limit_timeout') / 1000.0
    __limit_server_addr = (
        config.get('ad_server', 'limit_server_host'),
        config.getint('ad_server', 'limit_server_port'),
    )
    __udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    __udp_socket.settimeout(__limit_timeout)

    def get(self):
        '''根据输入参数 cid (Category ID, 由 Yahoo 提供) 来获取广告数据.

        参数 (从 HTTP GET 参数中获取):
            cid: Yahoo 提供的 Categroy ID
            limit: 返回广告条目数. 默认为 1, 最大为 10.
            os: 请求的客户端系统信息. Android 为 1, iOS 为 2.
            user_id: 唯一标识用户的 ID
        '''
        global ad_logger

        # 请求的 Category ID
        category_id = self.get_argument('cid', None)
        user_id = self.get_argument('uid', None)
        session_id = self.get_argument('sid', None)
        # Android: 1, iOS: 2
        # 默认为 Android
        os = self.get_argument('os', '1')
        # 请求的广告数目. 最大值为10, 默认值为 1
        limit = self.get_argument('lmt', self.__class__.__default_limit)
        limit = int(limit)
        limit = min(self.__class__.__max_limit, limit)

        ip = self.request.remote_ip
        ua = self.request.headers.get('User-Agent', None)
        errno = 0  # 错误码
        msg = ''  # 错误信息
        ad_data = None  # 广告数据
        if None in (category_id, user_id, session_id):  # 非法请求
            msg = 'invalid request'
            errno = 1
        else:
            ret = self.__limit_permit(user_id)
            if ret == 0:  # 不可访问
                errno = 4
                msg = 'qps forbid'
            elif ret == 1:  # 可以访问
                try:
                    ad_data = ydn.request(ip, ua, category_id, limit, os)
                except Exception as e:
                    errno = 3
                    msg = str(e)
                else:
                    if ad_data:
                        msg = 'ok'
                        errno = 0
                    else:
                        msg = 'invalid response'
                        errno = 3
            elif ret == 2:  # 用户达到上限
                errno = 5
                msg = 'user limit'
            elif ret == 3:  # 达到用户流量上限
                errno = 6
                msg = 'user stream limit'
            else:
                errno = 2
                msg = 'unknown error'

        # 每次请求都会记一条日志
        title, desc, url = None, None, None
        if errno == 0:
            title = ad_data["ads"][0]["title"].encode("utf-8")
            desc = ad_data["ads"][0]["description"].encode("utf-8")
            url = ad_data["ads"][0]["url"]

        log_string = ('ip={ip}, uid={uid}, sid={sid}, cid={cid}, lmt={lmt}, '
                      'os={os}, errno={errno}, msg={msg}, rt={rt:.3f}, '
                      'ua={ua}, tit={tit}, desc={desc}').format(
                ip=ip,
                uid=user_id,
                sid=session_id,
                cid=category_id,
                lmt=limit,
                os=os,
                errno=errno,
                msg=msg,
                rt=1000.0 * self.request.request_time(),
                ua=ua,
                tit=title,
                desc=desc,
        )
        ad_logger.info(log_string)

        # 返回结果
        ret_json = libs.utils.compose_ret(errno, ad_data)
        self.write(ret_json)

    def __limit_permit(self, user_id):
        # 发送用户 id
        try:
            self.__class__.__udp_socket.sendto(
                user_id, self.__class__.__limit_server_addr)
            data, addr = self.__class__.__udp_socket.recvfrom(1024)
        except Exception as e:
            ad_logger.error('info={}'.format(str(e)))
            return 0

        return int(data)
