# coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType



@allure.epic('我的班级')
@allure.feature('群聊')
@allure.story("发送文件")
@pytest.mark.myclass
@pytest.mark.groupmsg
class TestSendFile():

    @allure.title('发送群文件：上传文件-发送xlsx文件-历史消息查看发送的文件')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.repeat(50)
    def test_send_file(self, get_customerid, get_clazzid, get_groupidentifier):
        '''
        发送群文件：上传文件-发送xlsx文件-历史消息查看发送的文件
        '''
        filename = 'file.xlsx'
        info = apiinfo.get_upload_temp_file_info(apiinfo.getapi('FILE'), filename)
        res = req.req(info)
        # 返回的data应该是一个字典，且不能是空
        myassert.assert_json(res)
        myassert.json_key_should_not_equal_specified_value(res, 'data', {})

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()

        # 开始拼接文件发送参数
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = res['data']['fileType']
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['msgType'] = res['data']['fileType']
        del info_send['params']['messageContent']['imgMsg']
        info_send['params']['messageContent']['fileMsg'] = {}
        info_send['params']['messageContent']['fileMsg']['id'] = res['data']['id']
        info_send['params']['messageContent']['fileMsg']['fileName'] = filename
        info_send['params']['messageContent']['fileMsg']['url'] = res['data']['fileUrl']
        info_send['params']['messageContent']['fileMsg']['size'] = res['data']['fileSize']

        res2 = req.req(info_send)
        myassert.assert_json(res2)

        # 在历史消息中查看发送的消息
        myassert.assert_history_msg(get_groupidentifier, info_send['params']['messageContent']['fileMsg'])



if __name__ == '__main__':
    pytest.main()
