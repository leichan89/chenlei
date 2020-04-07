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
@allure.story("发送试卷")
@pytest.mark.myclass
@pytest.mark.groupmsg
class TestSendPaper():


    @allure.title('发送群试卷：查询试卷-随机发送试卷-查看试卷详情-历史消息中查看发送的试卷-下载答题详情')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_send_paper(self, get_customerid, get_clazzid, get_goodsid, get_groupidentifier):
        '''
        发送群试卷：查询试卷-随机发送试卷-查看试卷详情-历史消息中查看发送的试卷-下载答题详情
        '''
        # 查询试卷信息
        paper_list = apiinfo.getapi('paperList')
        paper_list['url'] = apiinfo.modify_url(paper_list, goodsId=get_goodsid)
        paper_list['params'] = None
        res = req.req(paper_list)
        myassert.assert_json(res)
        myassert.json_key_should_not_equal_specified_value(res, 'data', [])

        # 随机选择一个试卷
        paper_data = res['data']
        paper_data_info = paper_data[randint(0, len(paper_data) - 1)]

        info_send = apiinfo.getapi('sendMsgGroup')
        timestamp = tools.get_timestamp()
        info_send['params']['customerId'] = get_customerid
        info_send['params']['clazzId'] = get_clazzid
        info_send['params']['messageType'] = 'PAPER'
        info_send['params']['randomStr'] = timestamp
        info_send['params']['messageContent'] = {}
        info_send['params']['messageContent']['randomStr'] = timestamp
        info_send['params']['messageContent']['sendStatus'] = 'sending'
        info_send['params']['messageContent']['msgType'] = 'PAPER'
        info_send['params']['messageContent']['top'] = False
        info_send['params']['messageContent']['paperMsg'] = paper_data_info

        res2 = req.req(info_send)
        myassert.assert_json(res2)

        paper_info = apiinfo.getapi('paperScore')
        paper_info['url'] = apiinfo.modify_url(paper_info, clazzId=get_clazzid, paperId=paper_data_info['paperId'])

        # 查看试卷详情
        res3 = req.req(paper_info)
        myassert.assert_json(res3)

        # 在历史消息中查看发送的消息
        check_json = {'paperId': paper_data_info['paperId'], 'paperName': paper_data_info['paperName']}
        myassert.assert_history_msg(get_groupidentifier, check_json)

        # 下载推送的试卷的答题详情
        paper_record_info = apiinfo.getapi('getPaperRecordDetail')
        paper_record_info['params']['clazzId'] = get_clazzid
        paper_record_info['params']['paperId'] = paper_data_info['paperId']

        res4 = req.req(paper_record_info)
        assert res4, '下载试卷答题信息失败'

if __name__ == '__main__':
    pytest.main()
