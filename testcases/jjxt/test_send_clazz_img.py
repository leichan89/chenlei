#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType
from random import randint, shuffle


@allure.epic('我的班级')
@allure.feature('群聊')
@allure.story("发送图片")
@pytest.mark.myclass
@pytest.mark.groupmsg
class TestSendIMG():

    @allure.title('发送群图片：上传图片-发送jpg图片-历史消息查看发送的图片')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_send_img(self, get_customerid, get_clazzid, get_groupidentifier):
        '''
        发送群图片：上传图片-发送jpg图片-历史消息查看发送的图片
        '''
        filename = 'laoshi.jpg'
        info = apiinfo.get_upload_temp_file_info(apiinfo.getapi('IMG'), filename)
        res = req.req(info)
        myassert.assert_json(res)
        # 上传接口返回值的data应该是一个字典，且不是空
        myassert.json_key_should_not_equal_specified_value(res, 'data', {})

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()

        # 开始拼接发送图片参数
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = res['data']['fileType']
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['msgType'] = res['data']['fileType']
        info_send['params']['messageContent']['imgMsg']['type'] = res['data']['fileSuffix'].upper()
        info_send['params']['messageContent']['imgMsg']['imgInfo'][0]['id'] = res['data']['id']
        info_send['params']['messageContent']['imgMsg']['imgInfo'][0]['size'] = res['data']['fileSize']
        info_send['params']['messageContent']['imgMsg']['imgInfo'][0]['width'] = res['data']['width']
        info_send['params']['messageContent']['imgMsg']['imgInfo'][0]['height'] = res['data']['height']
        info_send['params']['messageContent']['imgMsg']['imgInfo'][0]['url'] = res['data']['fileUrl']
        res2 = req.req(info_send)
        myassert.assert_json(res2)

        # 在历史消息中查看发送的消息
        myassert.assert_history_msg(get_groupidentifier, info_send['params']['messageContent']['imgMsg'])


if __name__ == '__main__':
    pytest.main()
