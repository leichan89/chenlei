# coding=utf-8
import requests
from common.log import logger
from common.configer import GetConfiger


class GetSession():

    def __init__(self, username=None, password=None, redirect=None):
        self.username = username
        self.password = password
        configer = GetConfiger()
        cfg = configer.configer()
        self.url = cfg.get('env', 'loginurl') + '/ajaxLogin'
        if not redirect:
            self.redirect = cfg.get('env', 'redirect')
        else:
            self.redirect = redirect
        if not self.username:
            self.username = cfg.get('env', 'username')
        if not self.password:
            self.password = cfg.get('env', 'password')

    def session(self):
        logger.debug('开始登陆获取后台session')
        data = {'redirect': self.redirect, 'username': self.username, 'password': self.password, 'isNextLoad': 'true'}
        session = requests.session()
        try:
            ret = session.post(url=self.url, data=data)
            if ret.status_code == 200:
                token = ret.json()['data']
                jumprst = session.get('%s?token=%s' % (self.redirect, token))
                if jumprst.status_code == 200:
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


class StudySession(GetSession):

    def __init__(self):
        configer = GetConfiger()
        cfg = configer.configer()
        redirect = cfg.get('env', 'redirect_study')
        super().__init__(redirect=redirect)


class GetEndSession():

    def __init__(self):
        pass

    def endsession(self, data):
        esession = requests.session()
        headers = {"Content-Type": "application/x-www-form-urlencoded", 'Connection': 'close'}
        esession.post('http://t2.highso.com.cn/login.do', headers=headers, data=data)
        return esession

class GetAppSession():

    def __init__(self):
        pass

    def appsession(self):
        session = requests.session()
        return session

if __name__ == '__main__':
    s = StudySession()
    ss = s.session()
    rst = ss.get('https://api-study-web.reg.highso.com.cn/teacher/getTeacherStatistics')
    rst = rst.json()
    print(rst)
