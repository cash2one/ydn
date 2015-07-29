#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
封装读取配置的对象
默认文件位于 /conf/setting.cfg
'''
import ConfigParser
import os


__all__ = ['get_config', 'get_config_file', 'reload_config']
config = None
g_config_file = None


def get_config(config_file=None):
    global config, g_config_file

    # 使用默认配置文件
    if config_file is None:
        abs_path = os.path.abspath(os.path.dirname(__file__))
        g_config_file = os.path.join(abs_path, '../../conf/server.cfg')

    # 工厂模式，只有一个实例
    if config is None:
        config = ConfigParser.ConfigParser()
        config.read(g_config_file)

    return config


def get_config_file():
    global g_config_file

    get_config()
    return g_config_file


def reload_config():
    global config
    config = None

if __name__ == '__main__':
    conf = get_config()
    print conf.get('log', 'cid')
