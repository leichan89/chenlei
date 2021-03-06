#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType
from random import randint


@allure.epic('我的班级')
@allure.feature('群聊')
@allure.story("发送直播")
@pytest.mark.myclass
class TestSendLive():

    @allure.title('发送群直播：查询直播-随机发送回放直播-查询直播详情-历史消息中查看发送的直播')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_send_live_back(self, get_customerid, get_clazzid, get_goodsid, get_groupidentifier):
        '''
        发送群直播：查询直播-随机发送回放直播-查询直播详情-历史消息中查看发送的直播
        '''
        # 查询回放直播信息
        live_selector_list = apiinfo.getapi('liveSelectorList')
        live_selector_list['params']['status'] = 3
        live_selector_list['params']['liveStartTime'] = tools.get_date(-500)
        live_selector_list['params']['liveEndTime'] = tools.get_date()
        live_selector_list['params']['goodsId'] = get_goodsid
        res = req.req(live_selector_list)
        myassert.assert_json(res)
        myassert.json_key_should_not_equal_specified_value(res, 'data', [])

        # 随机选择一个直播回访记录
        live_data = res['data']
        live_data_info = live_data[randint(0, len(live_data) - 1)]

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = 'LIVE'
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent'] = {}
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['sendStatus'] = 'sending'
        info_send['params']['messageContent']['msgType'] = 'LIVE'
        info_send['params']['messageContent']['top'] = False
        info_send['params']['messageContent']['liveMsg'] = live_data_info

        res2 = req.req(info_send)
        myassert.assert_json(res2)

        view_live_info = apiinfo.getapi('studycontentGet')
        view_live_info['params']['clazzId'] = get_clazzid
        view_live_info['params']['businessId'] = live_data_info['liveId']
        view_live_info['params']['typeEnum'] = 'LIVE'

        # 查看发送到群里面的直播详情
        res3 = req.req(view_live_info)
        myassert.assert_json(res3)
        myassert.json_key_should_not_equal_specified_value(res3, 'clazzStudyContentLiveCustomerVos', [])

        # 在历史消息中查看发送的消息
        check_json = {'liveName': live_data_info['liveName'], 'liveId': live_data_info['liveId']}
        myassert.assert_history_msg(get_groupidentifier, check_json)

    @allure.title('发送群直播：查询直播-随机发送已结束直播-查询直播详情-历史消息中查看发送的直播')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_send_live_end(self, get_customerid, get_clazzid, get_goodsid, get_groupidentifier):
        '''
        发送群直播：查询直播-随机发送已结束直播-查询直播详情-历史消息中查看发送的直播
        '''
        # 查询已结束直播信息
        live_selector_list = apiinfo.getapi('liveSelectorList')
        live_selector_list['params']['status'] = 2
        live_selector_list['params']['liveStartTime'] = tools.get_date(-500)
        live_selector_list['params']['liveEndTime'] = tools.get_date()
        live_selector_list['params']['goodsId'] = get_goodsid
        res = req.req(live_selector_list)
        myassert.assert_json(res)
        myassert.json_key_should_not_equal_specified_value(res, 'data', [])

        # 随机选择一个已结束的直播
        live_data = res['data']
        live_data_info = live_data[randint(0, len(live_data) - 1)]

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = 'LIVE'
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent'] = {}
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['sendStatus'] = 'sending'
        info_send['params']['messageContent']['msgType'] = 'LIVE'
        info_send['params']['messageContent']['top'] = False
        info_send['params']['messageContent']['liveMsg'] = live_data_info

        # 发送直播
        res2 = req.req(info_send)
        myassert.assert_json(res2)

        view_live_info = apiinfo.getapi('studycontentGet')
        view_live_info['params']['clazzId'] = get_clazzid
        view_live_info['params']['businessId'] = live_data_info['liveId']
        view_live_info['params']['typeEnum'] = 'LIVE'

        # 查看发送到群里面的直播详情
        res3 = req.req(view_live_info)
        myassert.assert_json(res3)
        myassert.json_key_should_not_equal_specified_value(res3, 'clazzStudyContentLiveCustomerVos', [])

        # 在历史消息中查看发送的消息
        check_json = {'liveName': live_data_info['liveName'], 'liveId': live_data_info['liveId']}
        myassert.assert_history_msg(get_groupidentifier, check_json)


if __name__ == '__main__':
    pytest.main()
