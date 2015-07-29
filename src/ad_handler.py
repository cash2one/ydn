#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web
import lxml.etree
import requests
import socket

import libs


OS_ANDROID = 1
OS_IOS = 2
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
    '''

    config = libs.get_config()
    __ydn_host = config.get('ydn', 'host')
    __max_limit = config.getint('ydn', 'max_limit')
    __default_limit = config.getint('ydn', 'default_limit')
    __app_url = config.get('ydn', 'app_url')
    __encode = config.get('ydn', 'encode')
    __source_token_ios = config.get('ydn', 'source_token_ios')
    __source_token_android = config.get('ydn', 'source_token_android')
    __source_token_test = config.get('ydn', 'source_token_test')
    __android_append = config.get('ydn', 'android_append')
    __ios_append = config.get('ydn', 'ios_append')
    __limit_timeout = config.getint('ad_server', 'limit_timeout') / 1000.0
    __limit_server_addr = (
        config.get('ad_server', 'limit_server_host'),
        config.getint('ad_server', 'limit_server_port'),
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(__limit_timeout)

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
        # 请求的广告数目. 最大值为10, 默认值为 1
        limit = self.get_argument('lmt', self.__class__.__default_limit)
        limit = int(limit)
        limit = min(self.__class__.__max_limit, limit)
        # 系统. Android: 1, iOS: 2, 其余都非法, 非法请求都视为 Android
        os = self.get_argument('os', OS_ANDROID)
        if os != '2':  # 如果值不是2, 都视为 Android
            os = OS_ANDROID
        else:
            os = OS_IOS

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
                    ad_data = self.__request_ydn(category_id, limit, os)
                except Exception as e:
                    errno = 2
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
            'os={os}, errno={errno}, msg={msg}, rt={rt:.3f}, ua={ua}, '
            'tit={tit}, desc={desc}').format(
                ip=self.request.remote_ip,
                uid=user_id,
                sid=session_id,
                cid=category_id,
                lmt=limit,
                os=os,
                errno=errno,
                msg=msg,
                rt=1000.0 * self.request.request_time(),
                ua=self.request.headers.get('User-Agent', None),
                tit=title,
                desc=desc,
        )
        ad_logger.info(log_string)

        # 返回结果
        ret_json = libs.utils.compose_ret(errno, ad_data)
        self.write(ret_json)

    def __request_ydn(self, category_id, limit, os):
        '''请求 YDN 的数据

        YDN 需要如下参数:
            source: 广告接收方的标志符
            ctxtUrl: APP 的 Google Play URL
            outputCharEnc: 接收数据的编码格式, 请用 UTF-8
            affilData: 要一个 ip 与 ua 的连接字符串, 这里的 IP
                       必须要是真正的日本 IP, 同时, UA
                       中还需要在一个空格后附加如下信息:
                            iOS:        YJIAdSDK/XML
                            Android:    YJAd-ANDROID/XML
            maxCount: 最大请求数
            ctxtId: 请求的分类 id, 即 category_id

        参数:
            category_id: YDN 提供的 category_id
            limit: 请求返回的最大广告数
            os: 系统, 仅支持 OS_ANDROID 和 OS_IOS

        返回:
            返回处理好的广告列表, 形式为:
            [
                {
                    'rank': 1,
                    'title': 标题
                    'description': 描述
                    'url': 广告的链接
                },
                { ... },
                { ... },
                ...,
            ]
        '''
        # 准备数据
        # IP 和 UA 都使用用户的数据
        ip = self.request.remote_ip
        ua = self.request.headers['User-Agent']

        # 依据系统判断添加在后面的附加信息
        append = None
        source_token = None
        if os == OS_ANDROID:
            append = self.__class__.__android_append
            source_token = self.__class__.__source_token_android
        elif os == OS_IOS:
            append = self.__class__.__ios_append
            source_token = self.__class__.__source_token_ios
        else:
            # 因为前面已经处理过, 所以不会进入这个分支
            return
        affilData = 'ip={}&ua={} {}'.format(ip[0], ua[0], append)

        # 生成请求参数
        params = {
            'source': source_token,
            'ctxtUrl': self.__class__.__app_url,
            'outputCharEnc': self.__class__.__encode,
            'affilData': affilData,
            'maxCount': limit,
            'ctxtId': category_id,
        }
        response = requests.get(self.__class__.__ydn_host, params=params)
        # YDN 返回不是 200, 输出一条日志.
        if response.status_code != 200:
            info = 'YDN_NOT_200'
            log_string = 'info={}, affilData={}, ctxtId={}'.format(
                    info, affilData, ctxtId)
            ad_logger.error(log_string)
            raise Exception(info)

        text = response.text.encode("utf-8")
        ad_data = self.__parse_xml(text)
        return ad_data

    def __parse_xml(self, text):
        '''解析 YDN 返回的 XML 文件.

        返回:
            解析好的数据结构
        '''
        root = lxml.etree.fromstring(text)
        ad_data = []
        for listing in root[1][:-1]:
            url = listing[0].text
            desc = listing.attrib.get('description', None)
            title = listing.attrib.get('title', None)
            rank = listing.attrib.get('rank', None)
            try:
                rank = int(rank)
            except ValueError:
                pass
            ad_data.append({
                'title': title,
                'description': desc,
                'rank': rank,
                'url': url,
            })
        feedback = root[1][-1][0].text
        return {'ads': ad_data, 'feedback': feedback}

    def __limit_permit(self, user_id):
        # 发送用户 id
        try:
            self.__class__.sock.sendto(user_id, self.__class__.__limit_server_addr)
            data, addr = self.__class__.sock.recvfrom(1024)
        except Exception as e:
            ad_logger.error('info={}'.format(str(e)))
            return 0

        return int(data)
