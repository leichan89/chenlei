#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType


@allure.epic('我的班级')
@allure.feature('群聊')
@allure.story("发送文本")
@pytest.mark.myclass
@pytest.mark.text
class TestSendText:

    @allure.title('发送文本消息：发送文本消息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.repeat(50)
    def test_send_text(self, get_customerid, get_clazzid):
        '''
        发送群图片：发送文本消息：发送文本消息
        '''

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()

        # 开始拼接发送文本消息参数
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = 'TEXT'
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent'] = {}
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['sendStatus'] = 'sending'
        info_send['params']['messageContent']['msgType'] = 'TEXT'
        info_send['params']['messageContent']['top'] = False
        info_send['params']['messageContent']['textMsg'] = {}
        info_send['params']['messageContent']['textMsg']['callSomeone'] = False
        info_send['params']['messageContent']['textMsg']['callIdentifier'] = ""
        info_send['params']['messageContent']['textMsg']['callIdentifierNickName'] = ""
        info_send['params']['messageContent']['textMsg']['text'] = '群聊%s' % str(timestamp)

        res = req.req(info_send)
        myassert.assert_json(res)


if __name__ == '__main__':
    pytest.main()
