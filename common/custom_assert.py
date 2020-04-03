#coding=utf-8
import json
import threading
import time
from common.log import logger
from common.tools import tools


class Assert:

    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Assert, '_instance'):
            with Assert._instance_lock:
                if not hasattr(Assert, '_instance'):
                    Assert._instance = object.__new__(cls)
        return Assert._instance

    def assert_json(self, api_ret_json, check_json=None):
        """
        断言json类型返回值
        :param api_ret_json: 接口返回值
        :param check_json: 断言值
        :return:
        """
        errmsg = ''

        if not check_json:
            check_json = {'code': 200}

        tools.is_json(api_ret_json)
        tools.is_json(check_json)

        logger.info('\n断言值为:\n{check_json}\n响应信息:\n{api_ret_json}'.format(check_json=tools.format_json(check_json),
                                                                         api_ret_json=tools.format_json(api_ret_json)))
        try:
            for key in check_json.keys():
                api_ret_json_value = tools.get_nest_dict_value(api_ret_json, key, 'not_found_key')
                if api_ret_json_value == 'not_found_key':
                    errmsg = '响应json中未找到断言json中的key【%s】' % key
                    break
                if api_ret_json_value != check_json[key]:
                    errmsg = '断言接口返回值失败'
                    break
        except Exception as e:
            errmsg = 'json值异常 %s' % e
        finally:
            if errmsg:
                logger.error(errmsg)
                assert False, errmsg


    def app_assert_json(self, api_ret_json, check_json=None):
        '''
        断言app端返回值
        :param api_ret_json:
        :param check_json:
        :return:
        '''
        if not check_json:
            check_json = {"m": "ok", "s": 1}
        self.assert_json(api_ret_json, check_json=check_json)

    def assert_json_return_boolen(self, api_ret_json, check_json):
        """
        断言json类型返回值
        :param api_ret_json: 接口返回值
        :param check_json: 断言值
        :return:
        """

        tools.is_json(api_ret_json)
        tools.is_json(check_json)

        logger.info('\n断言值为:\n{check_json}\n响应信息:\n{api_ret_json}'.format(check_json=tools.format_json(check_json),
                                                                         api_ret_json=tools.format_json(api_ret_json)))
        try:
            for key in check_json.keys():
                api_ret_json_value = tools.get_nest_dict_value(api_ret_json, key, 'not_found_key')
                if api_ret_json_value == 'not_found_key':
                    return False
                if api_ret_json_value != check_json[key]:
                    return False
            return True
        except Exception as e:
            logger.debug('断言异常：\n%s' % e)
            return False


    def json_key_should_be_equal_specified_type(self, api_ret_json, key, key_type, log_res_json=False):
        '''
        判断返回的json中的某个key应等于指定类型的数据
        :param api_ret_json: 接口响应的json
        :param key: json的某个key
        :param key_type: 判断的类型
        :return: True
        '''

        if log_res_json:
            logger.info('响应信息:\n%s' % tools.format_json(api_ret_json))
        logger.info('断言json中指定的key【%s】的返回值类型必须是：【%s】' % (key, type(key_type)))
        ret = tools.get_nest_dict_value(api_ret_json, key, 'not_found_key')
        if ret == 'not_found_key':
            errmsg = '未找到名为【%s】的key' % key
            logger.error(errmsg)
        elif type(key_type) == type(ret):
            return
        else:
            errmsg = '指定的key【%s】的返回值类型必须是：【%s】' % (key, type(key_type))
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg

    def json_key_should_not_equal_specified_value(self, api_ret_json, key, ne_value, log_res_json=False):
        '''
        判断返回的json不能等于指定数据，但是类型必须与指定数据一致，空除外
        :param api_ret_json: 接口响应的json
        :param key: json的某个key
        :param ne_value: 不应等于的值
        :return: True
        '''

        if log_res_json:
            logger.info('响应信息:\n%s' % tools.format_json(api_ret_json))
        logger.info('断言json中指定的key【%s】的返回数据的类型必须是【%s】，'
                    '返回数据不能是【%s】' % (key, type(ne_value), ne_value))
        ret = tools.get_nest_dict_value(api_ret_json, key, 'not_found_key')
        if ret == 'not_found_key':
            errmsg = '未找到名为【%s】的key' % key
            logger.error(errmsg)
        elif type(ne_value) == type(ret):
            if ret != ne_value :
                return
            else:
                errmsg = '返回的数据不应等于：%s' % ne_value
                logger.error(errmsg)
        else:
            errmsg = '指定的key【%s】的返回值类型必须是：【%s】' % (key, type(ne_value))
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg


    def assert_history_msg(self,groupidentifier, check_json):
        from common.singleton_conf import apiinfo, req
        # 等待4s去查询群聊历史记录
        time.sleep(8)

        # 查询历史消息
        history_msg_info = apiinfo.getapi('historyMsg')
        history_msg_info['params']['groupIdentifier'] = groupidentifier
        history_msg_info['params']['startDate'] = tools.get_date(minutes=-2)
        history_msg_info['params']['endDate'] = tools.get_date(minutes=2)
        res4 = req.req(history_msg_info)

        self.assert_json(res4)
        self.json_key_should_not_equal_specified_value(res4, 'items', [])

        is_pass = False
        # 遍历历史消息，在历史消息中查找发送的消息
        for item in res4['data']['items']:
            try:
                info = json.loads(item['MsgBody'][0]['MsgContent']['Data'])
                if self.assert_json_return_boolen(info, check_json):
                    is_pass = True
                    break
            except:
                errmsg = '断言历史消息异常'
                logger.error(errmsg)
                assert False, errmsg
        assert is_pass, '历史消息中未找到发送的消息'

    def assert_history_msg_c2c(self,studentAccount, check_json):
        from common.singleton_conf import apiinfo, req
        # 等待4s去查询私聊历史记录
        time.sleep(8)

        # 查询历史消息
        history_msg_info = apiinfo.getapi('c2chistoryMsg')
        history_msg_info['params']['studentAccount'] = studentAccount
        history_msg_info['params']['startDate'] = tools.get_date(minutes=-2)
        history_msg_info['params']['endDate'] = tools.get_date(minutes=2)
        res4 = req.req(history_msg_info)

        self.assert_json(res4)
        self.json_key_should_not_equal_specified_value(res4, 'items', [])

        is_pass = False
        # 遍历历史消息，在历史消息中查找发送的消息
        for item in res4['data']['items']:
            try:
                info = json.loads(item['MsgBody'][0]['MsgContent']['Data'])
                if self.assert_json_return_boolen(info, check_json):
                    is_pass = True
                    break
            except:
                errmsg = '断言私聊历史消息异常'
                logger.error(errmsg)
                assert False, errmsg
        assert is_pass, '私聊历史消息中未找到发送的消息'

myassert = Assert()

if __name__ == '__main__':
    check = {
        "fileName": "file2.xlsx",
        "id": 2689,
        "size": 12655,
        "url": "https://imgstatic.highso.com.cn/jjxt/file/b450a551e491426482036f88ec78c788.xlsx?attname=file2.xlsx"
    }

    res = {
        "fileName": "file2.xlsx",
        "id": 2689,
        "pdf": False,
        "size": 12655,
        "url": "https://imgstatic.highso.com.cn/jjxt/file/b450a551e491426482036f88ec78c788.xlsx?attname=file2.xlsx",
        "viewUrl": ""
    }

    s = myassert.assert_json_return_boolen(res, check)
    print(s)
