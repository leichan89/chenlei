# coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType



@allure.epic('我的班级')
@allure.feature('私聊')
@allure.story("发送文本")
@pytest.mark.myclass
@pytest.mark.text
class TestSendPersonText():

    @allure.title('私聊发送文本消息：发送文本消息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.repeat(50)
    def test_send_person_text(self, get_customerid, get_clazzid, get_studentid):
        '''
        私聊发送文本消息：发送文本消息
        '''


        info_send = apiinfo.getapi('sendMsgPerson')
        info_send['url'] = apiinfo.modify_url(info_send, studentId=get_studentid)
        timestamp = tools.get_timestamp()

        # 开始拼接文件发送参数
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['studentId'] = get_studentid
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
        info_send['params']['messageContent']['textMsg']['text'] = '私聊%s' % str(timestamp)

        res = req.req(info_send)
        myassert.assert_json(res)




if __name__ == '__main__':
    pytest.main()
