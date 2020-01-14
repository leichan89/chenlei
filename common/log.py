#coding=utf-8
import logging
import os
import threading
import time
import configparser as cp
from logging.handlers import RotatingFileHandler


class Loger():

    _instance_lock = threading.Lock()

    def __init__(self):
        dir = os.path.dirname(os.path.dirname(__file__))
        cfg_path = dir + os.sep + 'config' + os.sep + 'log.ini'
        cfg = cp.ConfigParser()
        cfg.read(cfg_path)
        self.cfg = cfg
        self.log_path = dir + os.sep + 'log' + os.sep

    def __new__(cls, *args, **kwargs):
        if not hasattr(Loger, '_instance'):
            with Loger._instance_lock:
                if not hasattr(Loger, '_instance'):
                    Loger._instance = object.__new__(cls)
        return Loger._instance

    def getlogger(self):
        date = time.strftime('%Y-%m-%d', time.localtime())
        log_name = self.log_path + '%s-log.txt'%date
        max_bytes = int(self.cfg.get('log', 'max_bytes'))
        backup_count = int(self.cfg.get('log', 'backup_count'))
        log_level = int(self.cfg.get('log', 'log_level'))
        console = self.cfg.get('log', 'console')
        logfile = self.cfg.get('log', 'logfile')
        logger = logging.getLogger('jjxt')
        fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s')

        if console == 'on':
            ch = logging.StreamHandler()
            ch.setFormatter(fmt)
            logger.addHandler(ch)

        if logfile == 'on':
            fh = RotatingFileHandler(log_name, maxBytes=max_bytes, backupCount=backup_count)
            fh.setFormatter(fmt)
            logger.addHandler(fh)

        logger.setLevel(log_level)
        return logger

logger = Loger().getlogger()


if __name__ == '__main__':
    logger.warning("test")

