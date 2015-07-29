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
import os


class LimitServer(object):

    def __init__(self, config_file):
        self.__count = None
        self.__uid_dict = collections.defaultdict(lambda: 0)
        self.__config_file = config_file
        self.__config_mtime = os.path.getmtime(config_file)

        self.__load_config()
        self.__init_listener(self.__port)

    def __load_config(self):
        '''读取配置文件并完成所有配置
        '''
        config = ConfigParser.ConfigParser()
        config.read(self.__config_file)

        self.__qps = config.getint("limit_server", "qps")
        self.__qpd = config.getint("limit_server", "qpd")
        self.__max_user = config.getint("limit_server", "max_user")
        self.__port = config.getint("limit_server", "port")

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

    def __update_config(self):
        '''更新配置文件
        会自动判断文件是否修改过, 修改过才会改
        '''
        mtime = os.path.getmtime(self.__config_file)
        if mtime != self.__config_mtime:
            try:
                self.__load_config()
            except Exception as e:
                pass
            self.__config_mtime = mtime
            return True
        return False

    def __1s_loop(self):
        '''定时器任务: 清空每秒计数器
        '''
        # 判断是否需要读取配置文件
        # 如果配置文件发生了改变则重新初始化各参数
        self.__update_config()
        # qps 限制
        self.__count = self.__qps

        # 1 秒计时器循环
        self.__1s_timer = threading.Timer(1.0, self.__1s_loop)
        self.__1s_timer.start()

    def __1d_loop(self):
        '''定时任务: 清空每天用户访问量
        '''
        # 用户访问情况
        self.__uid_dict.clear()

        # 1 天计时器循环
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        tomorrow = now.replace(now.year, now.month, now.day, 0, 0, 0, 0) + \
                datetime.timedelta(days=1)
        time_delta = (tomorrow - now).total_seconds()
        self.__1d_timer = threading.Timer(time_delta, self.__1d_loop)
        self.__1d_timer.start()

    def __main_loop(self):
        '''主逻辑循环
        '''
        while 1:
            uid, addr = self.__listener.recvfrom(1024)
            if self.__uid_dict[uid] < self.__qpd:
                if self.__count:
                    # 先减少后返回, 保证实际 qps 小于等于设定值
                    self.__count -= 1
                    self.__uid_dict[uid] += 1
                    self.__listener.sendto('1', addr)  # 可以访问
                else:
                    self.__listener.sendto('0', addr)  # 不可访问
            else:
                self.__listener.sendto('2', addr)  # 用户达到上限

    def run(self):
        '''开启的入口
        '''
        self.__1s_loop()
        self.__1d_loop()
        self.__main_loop()


if __name__ == '__main__':
    limit_server = LimitServer('conf/server.cfg')
    limit_server.run()
