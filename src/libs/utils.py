#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import ujson


def compose_ret(errno, data=None):
    '''组成返回结果

    参数:
        errno: 错误编号
        data: 数据, 如果出错直接写出错误原因即可. 如果不写也有默认的 null

    返回:
        返回编码好的 json 字符串.
    '''
    ret = {'errno': errno, 'data': data}
    return ujson.dumps(ret)
