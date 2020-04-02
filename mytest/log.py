#coding=utf-8
import logging
import os
import time
import configparser as cp
from logging.handlers import RotatingFileHandler



'''
为什么要用log:

Python 中的 logging 模块可以让你跟踪代码运行时的事件，当程序崩溃时可以查看日志并且发现是什么引发了错误。
Log 信息有内置的层级——调试（debugging）、信息（informational）、警告（warnings）、错误（error）和严重错误（critical）。
你也可以在 logging 中包含 traceback 信息。不管是小项目还是大项目，都推荐在 Python 程序中使用 logging。当你运行一个 Python 脚本时，
你可能想要知道脚本的哪个部分在执行，并且检视变量的当前值。
'''


'''
日志级别：

级别排序:CRITICAL > ERROR > WARNING > INFO > DEBUG

debug : 打印全部的日志,详细的信息,通常只出现在诊断问题上

info : 打印info,warning,error,critical级别的日志,确认一切按预期运行

warning : 打印warning,error,critical级别的日志,一个迹象表明,一些意想不到的事情发生了,或表明一些问题在不久的将来(例如。磁盘空间低”),这个软件还能按预期工作

error : 打印error,critical级别的日志,更严重的问题,软件没能执行一些功能

critical : 打印critical级别,一个严重的错误,这表明程序本身可能无法继续运行
'''

'''
logger创建步骤：

# 1、创建一个logger 

# 2.1、创建一个handler，用于写入日志文件 

# 2.2、再创建一个handler，用于输出到控制台 

# 3、定义handler的输出格式（formatter）

# 4、给handler添加formatter

# 5、给logger添加handler 

'''

'''
xx
'''

class Loger():


    def __init__(self):
        # 获取当前文件所在目录的父目录
        dir = os.path.dirname(os.path.dirname(__file__))

        # 拼接日志文件配置目录绝对路径
        cfg_path = dir + os.sep + 'config' + os.sep + 'log.ini'

        # 创建读取配置文件的对象
        cfg = cp.ConfigParser()

        # 读取配置文件
        cfg.read(cfg_path)
        self.cfg = cfg

        # 设置存放日志文件的目录
        self.log_path = dir + os.sep + 'log' + os.sep

    def getlogger(self):
        # 设置日期格式
        date = time.strftime('%Y-%m-%d', time.localtime())

        # 设置日志文件的绝对路径，且日志文件的格式为：年-月-日-log.txt
        log_name = self.log_path + '%s-log.txt'%date

        # 设置单个日志文件的最大占用空间
        max_bytes = int(self.cfg.get('log', 'max_bytes'))

        # 日志最大分割数
        backup_count = int(self.cfg.get('log', 'backup_count'))

        # 设置日志级别，日志级别从配置文件中获取
        # 日志级别：critical=50, error=40, warning=30, info=20, debug=10
        log_level = int(self.cfg.get('log', 'log_level'))

        # 配置文件中是否在控制台打印日志的标记，如果是on则在控制台打印日志，不是则不打印
        console = self.cfg.get('log', 'console')

        # 配置文件中是否将日志记录到文件中的标记，如果是on则记录到日志文件中，不是则不记录
        logfile = self.cfg.get('log', 'logfile')

        # 创建日志记录器，名称可以自定义
        logger = logging.getLogger('jjxt')

        # 日志格式：2020-01-14 15:44:44,070 custom_assert.py[line:40] INFO:
        fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s')

        # 判断是否在控制台打印日志
        if console == 'on':
            # 日志流handler，日志信息会输出到指定的stream中
            ch = logging.StreamHandler()

            # 设置日志格式
            ch.setFormatter(fmt)

            # 将logger添加到handler里面
            logger.addHandler(ch)

        # 判断是否记录到日志文件
        if logfile == 'on':
            '''
            循环日志文件
            参数maxBytes和backupCount允许日志文件在达到maxBytes时rollover.当文件大小达到或者超过maxBytes时，
            就会新创建一个日志文件。上述的这两个参数任一一个为0时，rollover都不会发生。也就是就文件没有maxBytes限制。
            backupcount是备份数目，也就是最多能有多少个备份。命名会在日志的base_name后面加上.0-.n的后缀，
            如example.log.1,example.log.1,…,example.log.10。当前使用的日志文件为base_name.log。
            '''
            fh = RotatingFileHandler(log_name, maxBytes=max_bytes, backupCount=backup_count)
            fh.setFormatter(fmt)
            logger.addHandler(fh)

        # 设置日志级别
        logger.setLevel(log_level)
        return logger

# 创建日志实例
logger = Loger().getlogger()


if __name__ == '__main__':

    logger.setLevel(30)

    logger.debug('debug')
    logger.info('info')
    logger.warning("warning")
    logger.error('error')
    logger.critical('critical')

    try:
        1 / 0
    except Exception as e:
        logger.exception(e)
