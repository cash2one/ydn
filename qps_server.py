#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
使用 UDP 协议来控制 qps, 客户端可以获取到的结果有:
    '0': 不能访问
    '1': 可以访问
    超时: 不能访问
'''
import socket
import threading
import ConfigParser


class QpsServer(object):

    def __init__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)

        self.__qps = config.getint("qps_server", 'qps')
        port = config.getint("qps_server", "port")
        self.__init_listener(port)

        self.__count = None

    def run(self):
        '''开启的入口
        '''
        self.__clean()
        self.__loop()

    def __clean(self):
        '''定时器任务: 清空计数器
        '''
        self.__count = self.__qps
        self.__timer = threading.Timer(1.0, self.__clean)
        self.__timer.start()

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
            data, addr = self.__listener.recvfrom(1024)
            if self.__count:
                # 先减少后返回, 保证实际 qps 小于等于设定值
                self.__count -= 1
                self.__listener.sendto('1', addr)  # 可以访问
            else:
                self.__listener.sendto('0', addr)  # 不可访问


if __name__ == '__main__':
    qps_server = QpsServer('conf/server.cfg')
    qps_server.run()
