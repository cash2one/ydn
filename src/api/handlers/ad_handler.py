#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import tornado.web
import socket

import define
from .. import libs
from .. import ssp


ad_logger = libs.get_logger('ad')


class AdHandler(tornado.web.RequestHandler):
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
    '''


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
        try:
            os = int(os)
        except ValueError:
            os = define.OS_ANDROID

        ip = self.request.headers.get('clientip', None)
        ua = self.request.headers.get('User-Agent', None)
        errno = 0  # 错误码
        msg = ''  # 错误信息
        data = None  # 广告数据
        if None in (category_id, user_id, session_id):  # 非法请求
            errno = define.ERR_INVALID_PARAMS
            msg = define.MSG_INVALID_PARAMS
        else:
            try:
                ret = libs.limit.permit(user_id)
            except Exception as e:
                errno = define.ERR_AD_QPS_ERROR
                msg = str(e).replace('\n', ' ')
            else:
                if ret == define.LIMIT_ALLOW:
                    ydn_ssp = ssp.ydn_ssp.YdnSSP(category_id, os, ip, ua)
                    try:
                        data = ydn_ssp.get_ad()
                        errno = define.ERR_SUCCESS
                        msg = define.MSG_SUCCESS
                    except Exception as e:
                        errno = define.ERR_AD_SSP_ERROR
                        msg = define.MSG_AD_SSP_ERROR
                    else:
                        if data is None:
                            errno = define.ERR_AD_SSP_ERROR
                            msg = define.MSG_AD_SSP_ERROR
                        else:
                            errnor = define.ERR_SUCCESS
                            msg = define.MSG_SUCCESS
                elif ret == define.LIMIT_QPS_REFUSE:
                    errno = define.ERR_AD_QPS_LIMIT
                    msg = define.MSG_AD_QPS_LIMIT
                else:
                    errno = define.ERR_UNKNOWN_ERROR
                    msg = define.MSG_UNKNOWN_ERROR

        # 每次请求都会记一条日志
        title, desc, url = None, None, None
        if errno == 0:
            title = data["ads"][0]["title"].encode("utf-8")
            desc = data["ads"][0]["description"].encode("utf-8")
            url = data["ads"][0]["url"]

        log_string = ('ip={ip}\tuid={uid}\tsid={sid}\tcid={cid}\t'
                      'os={os}\terrno={errno}\tmsg={msg}\trt={rt:.3f}\t'
                      'ua={ua}\ttit={tit}\tdesc={desc}').format(
                ip=ip,
                uid=user_id,
                sid=session_id,
                cid=category_id,
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
        ret_json = libs.utils.compose_ret(errno, data)
        self.write(ret_json)
