#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import logging
import os

import config


conf = config.get_config()
has_inited = False
__all__ = ['get_logger']


def __init_file_handler(log_path, name):
    filename = os.path.join(log_path, conf.get('log', name + '_file'))
    file_handler = logging.FileHandler(filename, 'a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

def __init_logger(log_path):
    global conf

    fmt = '%(levelname)s %(asctime)s %(filename)s|%(lineno)d %(message)s'
    formatter = logging.Formatter(fmt)
    # requests
    requests_name = 'requests.packages.urllib3.connectionpool'
    requests_logger = logging.getLogger(requests_name)
    requests_logger.setLevel(logging.CRITICAL)
    # ad
    ad_filename = os.path.join(log_path, conf.get('log', 'ad_file'))
    ad_file_handler = logging.FileHandler(ad_filename, 'a')
    ad_file_handler.setLevel(logging.INFO)
    ad_file_handler.setFormatter(formatter)
    ad_logger = logging.getLogger('ad')
    ad_logger.addHandler(ad_file_handler)
    ad_logger.setLevel(logging.INFO)
    # cid
    cid_filename = os.path.join(log_path, conf.get('log', 'cid_file'))
    cid_file_handler = logging.FileHandler(cid_filename, 'a')
    cid_file_handler.setLevel(logging.INFO)
    cid_file_handler.setFormatter(formatter)
    cid_logger = logging.getLogger('cid')
    cid_logger.addHandler(cid_file_handler)
    cid_logger.setLevel(logging.INFO)
    # trace
    trace_filename = os.path.join(log_path, conf.get('log', 'trace_file'))
    trace_file_handler = logging.FileHandler(trace_filename, 'a')
    trace_file_handler.setLevel(logging.INFO)
    trace_file_handler.setFormatter(formatter)
    trace_logger = logging.getLogger('trace')
    trace_logger.addHandler(trace_file_handler)
    trace_logger.setLevel(logging.INFO)
    # root
    root_filename = os.path.join(log_path, conf.get('log', 'root_file'))
    root_file_handler = logging.FileHandler(root_filename, 'a')
    root_file_handler.setLevel(logging.WARNING)
    root_file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(root_file_handler)
    root_logger.setLevel(logging.INFO)


def __init_all():
    global conf, has_inited

    abs_path = os.path.abspath(os.path.dirname(__file__))
    # 根目录
    abs_root_path = os.path.join(abs_path, '../../')
    # log 目录
    log_path = conf.get('log', 'dir')
    log_path = os.path.join(abs_root_path, log_path)
    # 如果目录不存在就建立
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    # 初始化各种 logger
    __init_logger(log_path)
    has_inited = True


def get_logger(name=None):
    global has_inited

    if not has_inited:
        __init_all()

    return logging.getLogger(name)


if __name__ == '__main__':
    ad_logger = get_logger('ad')
    ad_logger.info("xixi")
    cid_logger = get_logger('cid')
    cid_logger.info("haha")
    root_logger = get_logger()
    root_logger.info("aaa")
    root_logger.warning("mmm")
