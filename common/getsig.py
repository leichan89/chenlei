#coding=utf-8
import jpype
import os
from common.log import logger
from common.configer import configer


class Sig():

    def __init__(self):
        dir = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'sig'
        self.sigclass = None
        try:
            jvmpath = jpype.getDefaultJVMPath()
            classpath = dir + os.sep + 'SigGenertor.class'
            jpype.startJVM(jvmpath, "-ea", "-Djava.class.path=%s" % classpath, "-Djava.ext.dirs=%s" % dir)
            self.sigclass = jpype.JClass('com.haixue.util.SigGenertor')
        except Exception:
            errmsg = '生成sign值异常'
            logger.error(errmsg)
            assert False, errmsg

    def get_url_include_sig(self, url, ios=False):
        if ios:
            self.sk = configer.configer().get('ios', 'salt')
        else:
            self.sk = configer.configer().get('andriod', 'salt')
        if self.sigclass:
            ret = self.sigclass.generate(url, self.sk)
            logger.debug('生成sig值成功： %s' % ret)
            url = url + '&sig=%s' % ret
            return url

sig = Sig()

if __name__ == "__main__":
    s = Sig()
    # url = "http://app-jjxt.reg.highso.com.cn/imMsg/getHistoryMsg.do?app_key=jr1t36ul&device=16th&rom=Flyme+7.3.0.0A&kernel=8.1.0&sk=bb1df88f-b978-4682-b54d-2f2f409a3d9a.1567402878145.11270365.awifi02:00:00:00:00:00.22320942c25f3500da8efc847e92ee45&token=awifi02%3A00%3A00%3A00%3A00%3A00&v=3.0&app_version=2.9.0&device_type=android"
    # url = s.get_url_include_sig(url)
    #
    # import requests
    #
    # data = {"studentImAccounts":["C-11270365"],"teacherImAccounts":["T-2157","T-2125","T-2159","T-2123"],"pageSize":"1","queryType":"C2C"}
    #
    #
    # res = requests.post(url, json=data)
    #
    # print(res.text)
    url = 'http://app-jjxt.reg.highso.com.cn/jjxt/v1/showPopup.do?app_key=jr1t36ul&device=16th&kernel=8.1.0&rom=Flyme 7.3.0.0A&sk=bb1df88f-b978-4682-b54d-2f2f409a3d9a.1567402878145.11270365.awifi02:00:00:00:00:00.22320942c25f3500da8efc847e92ee45&token=awifi02:00:00:00:00:00&v=3.0&app_version=2.9.0&device_type=android&classId=10699'

    print(s.get_url_include_sig(url))