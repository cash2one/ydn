#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import requests
import lxml.etree

import libs


OS_ANDROID = "1"
OS_IOS = "2"

config = libs.get_config()
HOST = config.get('ydn', 'host')
APP_URL = config.get('ydn', 'app_url')
ENCODE = config.get('ydn', 'encode')
SOURCE_TOKEN_IOS = config.get('ydn', 'source_token_ios')
SOURCE_TOKEN_ANDROID = config.get('ydn', 'source_token_android')
SOURCE_TOKEN_TEST = config.get('ydn', 'source_token_test')
ANDROID_APPEND = config.get('ydn', 'android_append')
IOS_APPEND = config.get('ydn', 'ios_append')

ad_logger = libs.get_logger('ad')


def parse_xml(text):
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
        sitehost = listing.attrib.get('siteHost', None)
        ad_data.append({
            'title': title,
            'description': desc,
            'rank': rank,
            'url': url,
            'sitehost': sitehost,
        })
    feedback = root[1][-1][0].text
    return {'ads': ad_data, 'feedback': feedback}


def request(ip, ua, category_id, limit, os):
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
                'sitehost': 广告连接的网址
            },
            { ... },
            { ... },
            ...,
        ]
    '''
    # 依据系统判断添加在后面的附加信息
    append = None
    source_token = None
    # 系统. Android: 1, iOS: 2, 其余都非法, 非法请求都视为 Android
    if os == OS_IOS:
        append = IOS_APPEND
        source_token = SOURCE_TOKEN_IOS
    else:
        append = ANDROID_APPEND
        source_token = SOURCE_TOKEN_ANDROID

    affilData = 'ip={}&ua={} {}'.format(ip, ua, append)

    # 生成请求参数
    params = {
        'source': source_token,
        'ctxtUrl': APP_URL,
        'outputCharEnc': ENCODE,
        'affilData': affilData,
        'maxCount': limit,
        'ctxtId': category_id,
    }
    response = requests.get(HOST, params=params)
    # YDN 返回不是 200, 输出一条日志.
    if response.status_code != 200:
        info = 'YDN_NOT_200'
        log_string = 'info={}, affilData={}, ctxtId={}'.format(
                info, affilData, ctxtId)
        ad_logger.error(log_string)
        raise Exception(info)

    text = response.text.encode("utf-8")
    print text
    ad_data = parse_xml(text)
    return ad_data
