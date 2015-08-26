#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
'''
封装读取配置的对象
默认文件位于 /conf/setting.cfg
'''
import ConfigParser
import os


__all__ = ['get_config', 'reload_config']
config = None


def get_config(config_file=None):
    global config

    # 使用默认配置文件
    if config_file is None:
        abs_path = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(abs_path, '../../../conf/ssp.cfg')

    # 工厂模式，只有一个实例
    if config is None:
        config = ConfigParser.ConfigParser()
        config.read(config_file)

    return config


def reload_config():
    global config
    config = None


if __name__ == '__main__':
    conf = get_config()
    print conf.get('redis', 'host')
