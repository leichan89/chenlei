#coding=utf-8
import os
import configparser as cp
from mytest.log import logger


class GetConfiger():

    '''

    该模块适用于配置文件的格式与windows ini文件类似，可以包含一个或多个节（section），每个节可以有多个参数（键=值）

    [DEFAULT]
    ServerAliveInterval = 45
    Compression = yes
    CompressionLevel = 9
    ForwardX11 = yes

    [bitbucket.org]
    User = Atlan
    '''

    '''
    步骤
    1、确定需要读取的配置文件的路径
    2、根据节点读取参数
    '''

    def __init__(self, file=None):
        # 配置文件所在路径
        cfgdir = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'config' + os.sep

        # 创建读取配置文件的对象
        cfg = cp.ConfigParser()
        if file:
            cfg_path = cfgdir + file
        else:
            env = cfgdir + 'env.ini'

            # 读取配置文件，包括所有section，和option
            cfg.read(env)
            cfg_path = cfgdir + 'envconf' + os.sep + cfg.get('env', 'env') + '.ini'

        logger.info(cfg_path)



if __name__ == '__main__':
    g = GetConfiger()