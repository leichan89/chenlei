# coding=utf-8
import requests
import json
from common.log import logger
from common.configer import configer
from common.tools import tools
from urllib.parse import urlencode
from common.singleton_conf import apiinfo


class GetSession():


    '''
    1、读取配置中的登陆地址和用户名、密码
    2、拼接登陆请求的body
    3、向ucenter发送post请求
    4、获取ucenter响应的token信息
    5、访问重定向地址，并传入token信息
    6、返回session

    '''

    def __init__(self, username=None, password=None):
        cfg = configer.configer()
        # 从配置文件中获取登陆的地址
        self.url = cfg.get('env', 'loginurl') + '/ajaxLogin'
        logger.info(self.url)

        # 从配置文件获取登陆的重定向地址
        self.redirect = cfg.get('env', 'redirect')
        logger.info(self.redirect)

        # 从配置文件获取登陆的用户名
        self.username = cfg.get('env', 'username')
        logger.info(self.username)

        # 从配置文件获取登陆的用户密码
        self.password = cfg.get('env', 'password')
        logger.info(self.password)

    def session(self):
        logger.debug('开始登陆')

        # 登陆请求的body
        data = {'redirect': self.redirect, 'username': self.username, 'password': self.password, 'isNextLoad': 'true'}
        logger.info(data)
        session = requests.session()
        try:
            # 开始访问登陆地址，登陆ucenter
            ret = session.post(url=self.url, data=data)

            # 判断登陆的状态吗是否等于200
            if ret.status_code == 200:

                # 从响应结果中获取token信息
                token = ret.json()['data']

                # 开始访问重定向地址，重定向到教务后台
                logger.info('%s?token=%s' % (self.redirect, token))
                jumprst = session.get('%s?token=%s' % (self.redirect, token))

                # 判断是否跳转成功
                if jumprst.status_code == 200:

                    # 返回登陆成功的session
                    logger.info(jumprst.content)
                    return session
                else:
                    errmsg = '登陆跳转失败'
                    logger.error(errmsg)
            else:
                errmsg = '登陆失败，状态码为：%s' % ret.status_code
                logger.error(errmsg)
        except Exception as err:
            if str(err).find('Failed to establish a new connection') != -1:
                errmsg = '访问登陆接口失败，未能建立连接，请检查接口地址或网络环境是否OK'
                logger.error(errmsg)
            else:
                errmsg = '登陆发生异常\n%s' % str(err)
                logger.error(errmsg)
        if errmsg:
            assert False, errmsg

class MyRequests:


    '''
    1、初始化，获取登陆返回的session
    2、读取配置信息
    3、解析从excel中获取到的接口信息，主要是接口的地址、参数
    4、调用不同方法，get\psot\form
    4.1、向get方法传入接口地址，请求参数类型params：一个字典
    4.2、向post方法传入接口地址，请求参数类型最好用data：最好是一个json格式的字符串
    4.3、向post-form方法传入接口地址，请求参数类型是params：一个字典（需要转换None、True、False为null、true、false）
    5、返回接口响应的信息
    '''

    def __init__(self):
        self.cfg = configer.configer()
        self.session = GetSession().session()
        self.endpoint = self.cfg.get('env', 'endpoint')

    def myget(self, info):
        logger.info('发送get请求')

        # 解析excel中的请求参数信息
        params = info['params']
        if params:
            if isinstance(params, dict):
                logger.info('请求参数信息为\n%s' % tools.format_json(params))
            else:
                errmsg = "get请求的参数必须是字典类型或者为空"
                logger.error(errmsg)
        # get请求需要传入接口的地址，请求头，参数（params），参数可以一个字典，也可以直接写到url里面，推荐使用字典
        ret = self.session.get(url=self.endpoint + info['url'], headers=info['headers'], params=params)
        return ret

    def mypost(self, info):
        logger.info('发送post请求')
        data = info['data']
        try:
            logger.info('请求参数信息为\n%s' % tools.format_json(data))
            '''
            1、json参数：不管传入的参数是str类型还是dict类型，如果不指定headers中的content-type，默认为application/json
            2、data参数：data为dict时，如果不指定content-type，默认为application/x-www-form-urlencoded，相当于普通form表单提交的形式
            3、data为str时，如果不指定content-type，默认为application/json
            推荐使用将字典转换为json格式的字符串使用，因为涉及到下载的如果使用json参数，会抛异常
            '''
            # 将字典转换成json格式的字符串，会自动替换字典中的None、True、False为null、true、false
            # 因为Content-Type: application/json格式的post请求参数要是json格式的，在python
            # 中None、True、False是不能被识别的，需要转换成json格式的null、true、false

            # 也可以不将参数转转为json格式的字符串，使用post(url=self.endpoint + info['url'], headers=info['headers'], json=data)
            data = json.dumps(data)

        except:
            logger.debug('将json转换为字符失败')

        # post请求需要传入接口的地址，请求头，参数(data)，参数必须是json格式的字符串类型
        ret = self.session.post(url=self.endpoint + info['url'], headers=info['headers'], data=data)
        return ret

    def mypost_form(self, info):
        logger.info('发送post_form请求')
        params = info['params']
        if params:
            if isinstance(params, dict):
                logger.info('请求参数信息为\n%s' % tools.format_json(params))
                # 将字典类型转换为query参数，适用于请求格式是"application/x-www-form-urlencoded"的表单数据，类似get请求
                # 转换前需要替换字典中的None、True、False为null、true、false，并且返回一个字典
                # 因为urlencode传入必须是一个字典
                logger.info(self._format_json_data(info['params']))
                params = urlencode(self._format_json_data(info['params']))
            else:
                errmsg = "post_form请求的参数必须是字典类型或者为空"
                logger.error(errmsg)
        ret = self.session.post(url=self.endpoint + info['url'], headers=info['headers'], params=params)
        return ret


    # 将表单请求中的单引号转为双引号，None转为null，False转为false，将True转为true
    # 因为form参数中不能识别python中的True和False、None
    def _format_json_data(self, data):
        temp_data = data
        for k, v in temp_data.items():
            if isinstance(v, dict):
                self._format_json_data(v)
            else:
                if isinstance(v, bool) or v is None:
                    v = str(v)
                    v = v.replace('\'', '\"').replace('None', 'null').replace('False', 'false').replace('True', 'true')
                    temp_data[k] = v
                else:
                    temp_data[k] = v
        return temp_data


if __name__ == '__main__':
    my = MyRequests()
    myapi_info = apiinfo.getapi('clazzTypesSearch')
    ret = my.myget(myapi_info)

    print(ret.json())