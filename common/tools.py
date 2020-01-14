#coding=utf-8
import datetime
import threading
import json
import os
import time
import mimetypes
from common.log import logger


class Tools():

    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Tools, '_instance'):
            with Tools._instance_lock:
                if not hasattr(Tools, '_instance'):
                    Tools._instance = object.__new__(cls)
        return Tools._instance

    def is_json(self, api_ret_json):
        '''
        判断是否是json格式数据
        :param api_ret_json: 参数
        :return:
        '''
        if not isinstance(api_ret_json, dict):
            errmsg = '返回值不是有效的json\n%s' % api_ret_json
            logger.error(errmsg)
            assert False, errmsg

    def get_nest_dict_value(self, d, objkey, default=None):
        """
        获取字典中的objkey对应的值，适用于字典嵌套
        :param d: 字典对象
        :param objkey: 目标key
        :param default: 找不到时返回的默认值
        :return:
        """
        tmp = d
        for k, v in tmp.items():
            if k == objkey:
                return v
            else:
                if isinstance(v, dict):
                    ret = self.get_nest_dict_value(v, objkey, default)
                    if ret is not default:
                        return ret
        return default

    def format_json(self, target_json):
        '''
        格式化json样式
        :param target_json:目标json
        :return:格式化后的json
        '''
        try:
            target_json = json.dumps(target_json, ensure_ascii=False, sort_keys=True, indent=2)
        except:
            logger.debug('不是有效的json数据')
        finally:
            return target_json

    def get_temp_path(self, filename):
        filepath = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'temp' + os.sep + filename
        if os.path.exists(filepath):
            return filepath
        else:
            errmsg = '%s 文件不存在' % filename
            logger.error(errmsg)
            assert False, errmsg

    def get_timestamp(self, year=None, month=None, day=None, hour=None, minute=None, second=None):
        '''
        默认获取当前时间
        :param year: 年
        :param month: 月
        :param day: 日
        :return: 时间戳
        '''
        mytime = datetime.datetime.now()
        if not year:
            year = mytime.year
        if not month:
            month = mytime.month
        if not day:
            day = mytime.day
        if not hour:
            hour = mytime.hour
        if not minute:
            minute = mytime.minute
        if not second:
            second = mytime.second
        if isinstance(year, int) and isinstance(month, int) and isinstance(day, int) and \
                isinstance(hour, int) and isinstance(minute, int) and isinstance(second, int):
            try:
                mytime = datetime.datetime(year, month, day, hour, minute, second)
                timearray = time.strptime(str(mytime), "%Y-%m-%d %H:%M:%S")
                timestamp = int(time.mktime(timearray)) * 1000
                return timestamp
            except:
                errmsg = '转换时间戳异常，请检查参数'
                logger.error(errmsg)
        else:
            errmsg = '年月日必须是整数'
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg


    def get_date(self, days=0, hours=0, minutes=0, seconds=0, h_m_s=True):
        '''
        生成指定日期时间，可以是之前的或者之后的日期，默认生成当前日期
        :param days: 天数
        :param hours: 小时
        :param minutes: 分钟
        :param seconds: 秒
        :return:
        '''
        try:
            now = datetime.datetime.now()
            delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            n_days = now + delta
            if h_m_s:
                return n_days.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return n_days.strftime('%Y-%m-%d')
        except:
            errmsg = '生成日期异常, days, hours, minutes, seconds必须是整数'
            logger.error(errmsg)
            assert False, errmsg


    def get_file_mimetype(self, filepath):
        if os.path.exists(filepath):
            file_mimetype = mimetypes.guess_type(filepath)[0]
            if file_mimetype:
                return file_mimetype
            else:
                errmsg = '获取文件MIME类型失败'
                logger.error(errmsg)
        else:
            errmsg = '文件路径错误'
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg

    def params_to_dict(self, params):
        params_dict = {}
        try:
            if params:
                param = params.split('&')
                if param:
                    for p in param:
                        key_value = p.split('=')
                        if len(key_value) == 2:
                            if key_value[1] == "":
                                key_value[1] = ""
                            params_dict[key_value[0]] = key_value[1]
                        elif len(key_value) == 1:
                            params_dict[key_value[0]] = ""
        except:
            pass
        return params_dict


tools = Tools()


class AllureCaseType:
    '''
    BLOCKER          级别：中断缺陷（客户端程序无响应，无法执行下一步操作)
    CRITICAL         级别：临界缺陷（功能点缺失）
    NORMAL           级别：普通缺陷（数值计算错误）
    MINOR            级别：次要缺陷（界面错误与UI需求不符）
    TRIVIAL          级别：轻微缺陷（必输项无提示，或者提示不规范)
    '''
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    MINOR = 'minor'
    TRIVIAL = 'trivial'


if __name__ == '__main__':
    s = 'clazzId=438&studentLevel=&paperId=4905'

    print(tools.params_to_dict(s))