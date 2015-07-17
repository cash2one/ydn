#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
使用 UDP 协议来控制 qps, 客户端可以获取到的结果有:
    '0': 不能访问
    '1': 可以访问
    '2': 用户访问次数达到上限
    超时: 不能访问
'''
import socket
import threading
import ConfigParser
import collections
import datetime


class LimitServer(object):

    def __init__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        self.__qps = config.getint("limit_server", "qps")
        qpd = config.getint("limit_server", "qpd")
        port = config.getint("limit_server", "port")

        self.__count = None
        self.__uid_dict = collections.defaultdict(lambda: qpd)
        self.__init_listener(port)

    def run(self):
        '''开启的入口
        '''
        self.__clean_qps()
        self.__clean_qpd()
        self.__loop()

    def __clean_qps(self):
        '''定时器任务: 清空计数器
        '''
        self.__count = self.__qps

        self.__1m_timer = threading.Timer(1.0, self.__clean_qps)
        self.__1m_timer.start()

    def __clean_qpd(self):
        self.__uid_dict.clear()

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        tomorrow = now.replace(now.year, now.month, now.day, 0, 0, 0, 0) + \
                datetime.timedelta(days=1)
        time_delta = (tomorrow - now).total_seconds()
        self.__1d_timer = threading.Timer(time_delta, self.__clean_qpd)
        self.__1d_timer.start()

    def __init_listener(self, port):
        '''初始化监听 socket

        使用 UDP 协议的 socket
        '''
        self.__listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listener.bind(('', port))

    def __loop(self):
        '''主逻辑循环
        '''
        while 1:
            uid, addr = self.__listener.recvfrom(1024)
            if self.__uid_dict[uid] > 0:
                if self.__count:
                    # 先减少后返回, 保证实际 qps 小于等于设定值
                    self.__count -= 1
                    self.__uid_dict[uid] -= 1
                    self.__listener.sendto('1', addr)  # 可以访问
                else:
                    self.__listener.sendto('0', addr)  # 不可访问
            else:
                self.__listener.sendto('2', addr)  # 用户达到上限



if __name__ == '__main__':
    limit_server = LimitServer('conf/server.cfg')
    limit_server.run()
