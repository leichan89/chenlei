#coding=utf-8
import os
import threading
import configparser as cp
from common.log import logger


class GetConfiger():

    def __init__(self, file=None):
        errmsg = ''
        cfgdir = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config' + os.sep
        cfg = cp.ConfigParser()
        if file:
            self.cfg_path = cfgdir + file
        else:
            env = cfgdir + 'env.ini'
            cfg.read(env)
            self.cfg_path = cfgdir + 'envconf' + os.sep + cfg.get('env', 'env') + '.ini'

        if os.path.exists(self.cfg_path):
            logger.debug('读取配置文件 %s' % self.cfg_path)
            try:
                cfg.read(self.cfg_path)
                self.cfg = cfg
            except:
                errmsg = '读取配置文件异常'
                logger.error(errmsg)
        else:
            errmsg = '配置文件路径无效'
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg

    def configer(self):
        return self.cfg

    def filepath(self):
        return self.cfg_path


# 默认读取env.ini文件
configer = GetConfiger()



if __name__ == '__main__':
    pass