#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
import logging
import logging.handlers
import os
import time

import config


conf = config.get_config()
has_inited = False
__all__ = ['get_logger']

class MultiProcessingTimedRotatingFileHandler(
        logging.handlers.TimedRotatingFileHandler):

    def doRollover(self):
        '''直接复制了 TimedRotatingFileHandler 中的函数,
        修改了部分
        '''
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            # find the oldest log file and delete it
            #s = glob.glob(self.baseFilename + ".20*")
            #if len(s) > self.backupCount:
            #    s.sort()
            #    os.remove(s[0])
            for s in self.getFilesToDelete():
                os.remove(s)
        #print "%s -> %s" % (self.baseFilename, dfn)
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt


def __init_logger(log_path):
    global conf

    fmt = '%(levelname)s %(asctime)s %(filename)s|%(lineno)d\t%(message)s'
    formatter = logging.Formatter(fmt)
    when = 'MIDNIGHT'
    interval = 1
    backup_count = 0
    # requests
    requests_name = 'requests.packages.urllib3.connectionpool'
    requests_logger = logging.getLogger(requests_name)
    requests_logger.setLevel(logging.CRITICAL)
    # ad
    ad_filename = os.path.join(log_path, conf.get('log', 'ad_file'))
    ad_file_handler = MultiProcessingTimedRotatingFileHandler(
            ad_filename, when=when, interval=interval, backupCount=backup_count)
    ad_file_handler.setLevel(logging.INFO)
    ad_file_handler.setFormatter(formatter)
    ad_logger = logging.getLogger('ad')
    ad_logger.addHandler(ad_file_handler)
    ad_logger.setLevel(logging.INFO)
    # cid
    cid_filename = os.path.join(log_path, conf.get('log', 'cid_file'))
    cid_file_handler = MultiProcessingTimedRotatingFileHandler(
            cid_filename, when=when, interval=interval, backupCount=backup_count)
    cid_file_handler.setLevel(logging.INFO)
    cid_file_handler.setFormatter(formatter)
    cid_logger = logging.getLogger('cid')
    cid_logger.addHandler(cid_file_handler)
    cid_logger.setLevel(logging.INFO)
    # trace
    trace_filename = os.path.join(log_path, conf.get('log', 'trace_file'))
    trace_file_handler = MultiProcessingTimedRotatingFileHandler(
            trace_filename, when=when, interval=interval, backupCount=backup_count)
    trace_file_handler.setLevel(logging.INFO)
    trace_file_handler.setFormatter(formatter)
    trace_logger = logging.getLogger('trace')
    trace_logger.addHandler(trace_file_handler)
    trace_logger.setLevel(logging.INFO)
    # root
    root_filename = os.path.join(log_path, conf.get('log', 'root_file'))
    root_file_handler = MultiProcessingTimedRotatingFileHandler(
            root_filename, when=when, interval=interval, backupCount=backup_count)
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
