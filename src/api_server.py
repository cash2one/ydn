#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
使用 tornado 作为服务器, 因为服务是多台机器混布的, 机器上重新配置 stackless
环境麻烦且不是很稳定 (怕 stackless 会和 original python 有冲突). 而且, tornado
已经在多台机器上布好了.

需要安装以下依赖库:

1. tornado      我比较喜爱的一个 HTTP 服务器框架, 采用异步结构, 使用 epoll,
                效率比较高.
2. requests     官方的描述是 "给人读的 HTTP 请求库. 使用方法比较友善,
                效率主要还是看网络.
3. ultrajson    效率非常高的 JSON 库, 详细评测可以看:
                https://medium.com/@jyotiska/json-vs-simplejson-vs-ujson-a115a63a9e26
4. lxml         lxml 是基于 C 库 libxml2 来实现的, 所以效率非常高的 XML 解析库,
                详细评测可以看: http://www.yakergong.net/blog/archives/487
                安装 lxml 需要 libxslt-devel.
5. redis        redis 的 Python 接入库, 主页: https://pypi.python.org/pypi/redis

安装方法: pip install tornado requests ujson lxml redis
'''
import tornado.ioloop
import tornado.web
import tornado.httpserver

import api.libs
import api.handlers


def run_server():
    '''初始化服务器
    '''
    # 仅 2 个 URI
    application = tornado.web.Application([
        (r"/ad", api.handlers.AdHandler),
        (r"/cid", api.handlers.CidHandler),
        (r"/trace", api.handlers.TraceHandler),
        (r"/predict", api.handlers.PredictHandler),
    ])

    config = api.libs.get_config()
    port = config.getint('api_server', 'port')
    server = tornado.httpserver.HTTPServer(application)
    server.bind(port)
    # 多进程模式
    server.start(0)

    # 开始跑
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    run_server()
