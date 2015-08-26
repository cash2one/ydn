#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
使用 UDP 协议来控制 qps, 客户端可以获取到的结果有:
'''
import socket
import threading
import mutex
import api.libs
import api.handlers.define



class LimitServer(object):

    def __init__(self):
        self.__count = 0
        self.__mutex = threading.Lock()

        conf = api.libs.get_config()
        port = conf.getint("limit_server", "port")
        self.__init_listener(port)

        self.__qps = conf.getint("limit_server", "qps")

    def __init_listener(self, port):
        '''初始化监听 socket

        使用 UDP 协议的 socket
        '''
        try:
            self.__listener.close()
        except Exception as e:
            pass
        self.__listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__listener.bind(('', port))

    def __1s_loop(self):
        '''定时器任务: 清空每秒计数器
        '''
        # qps 限制
        self.__mutex.acquire()
        self.__count = 0
        self.__mutex.release()

        # 1 秒计时器循环
        self.__1s_timer = threading.Timer(1.0, self.__1s_loop)
        self.__1s_timer.start()

    def __main_loop(self):
        '''主逻辑循环
        '''
        while 1:
            uid, addr = self.__listener.recvfrom(1024)
            if self.__count < self.__qps:
                self.__mutex.acquire()
                self.__count += 1
                self.__mutex.release()
                self.__listener.sendto(api.handlers.define.LIMIT_ALLOW, addr)
            else:
                self.__listener.sendto(api.handlers.define.LIMIT_QPS_REFUSE, addr)

    def run(self):
        '''开启的入口
        '''
        self.__1s_loop()
        self.__main_loop()


if __name__ == '__main__':
    limit_server = LimitServer()
    limit_server.run()
