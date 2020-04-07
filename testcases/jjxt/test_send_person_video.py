#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import tools
from common.tools import AllureCaseType
from random import shuffle


@allure.epic('我的班级')
@allure.feature('私聊')
@allure.story("发送录播")
@pytest.mark.myclass
@pytest.mark.c2cmsg
class TestSendPersonVideo():

    @allure.title('私聊发送录播：查询科目-查询模块-查询录播-向单个学员随机发送录播-查询录播详情-在历史消息中查看发送的录播')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_send_person_video(self, get_customerid, get_clazzid, get_goodsid, get_studentid, get_studentcid):
        '''
        私聊发送录播：查询科目-查询模块-查询录播-向单个学员随机发送录播-查询录播详情-在历史消息中查看发送的录播
        '''
        all_pass = False
        # 查询科目信息
        subject_list_info = apiinfo.getapi('subjectList')
        subject_list_info['url'] = apiinfo.modify_url(subject_list_info, goodsId=get_goodsid)
        res = req.req(subject_list_info)
        myassert.assert_json(res)
        # 返回的data应该是一个列表，且不能是空
        myassert.json_key_should_not_equal_specified_value(res, 'data', [])

        # 获取科目的信息
        subject_list = res['data']

        # 打乱科目信息
        shuffle(subject_list)

        # 遍历所有可以，当科目下能找到录播且能正常发送，则用例通过
        for sub in subject_list:
            subject_id = sub['id']
            # 查询模块信息
            module_list_info = apiinfo.getapi('moduleList')
            module_list_info['url'] = apiinfo.modify_url(module_list_info, goodsId=get_goodsid)
            module_list_info['params']['subjectId'] = subject_id
            module_list_info['params']['moduleType'] = 'VIDEO'
            res2 = req.req(module_list_info)
            # 查询的模块信息data必须是列表，但是可以是空，为空时跳出循环，查询下一个科目是否为空
            myassert.json_key_should_be_equal_specified_type(res2, 'data', [], log_res_json=True)

            module_data = res2['data']
            # 判断模块是否等于0
            if len(module_data) == 0:
                continue
            video_selector_list_info = apiinfo.getapi('videoSelectorList')
            # 拼接参数，获取整个科目下的所有录播数据
            for d in module_data:
                video_selector_list_info['params']['moduleIds[%s]' % module_data.index(d)] = d['id']

            # 根据科目信息下所有的模块信息查询录播信息
            res3 = req.req(video_selector_list_info)
            # 信息可以为空，但是必须是列表类型
            myassert.json_key_should_be_equal_specified_type(res3, 'data', [], log_res_json=True)
            
            video_data = res3['data']
            # 判断是否查询到录播信息，查询不到就跳出循环，查询下一个
            if len(video_data) == 0:
                continue
            # 遍历录播信息，只要能发送则中断循环
            for video_base_info in video_data:
                # 开始拼接录播发送接口参数
                video_subjectname = video_base_info['subject']['subjectName']
                video_subjectId = video_base_info['subject']['id']
                video_muduleList = [i['name'] for i in video_base_info['muduleList']]

                timestamp = tools.get_timestamp()
                info_send = apiinfo.getapi('sendMsgPerson')
                info_send['url'] = apiinfo.modify_url(info_send, studentId=get_studentid)
                info_send['params']['customerId'] = get_customerid
                info_send['params']['clazzId'] = get_clazzid
                info_send['params']['studentId'] = get_studentid
                info_send['params']['messageType'] = 'VIDEO'
                info_send['params']['randomStr'] = timestamp
                info_send['params']['messageContent'] = {}
                info_send['params']['messageContent']['randomStr'] = timestamp
                info_send['params']['messageContent']['sendStatus'] = 'sending'
                info_send['params']['messageContent']['msgType'] = 'VIDEO'
                info_send['params']['messageContent']['top'] = False
                info_send['params']['messageContent']['videoMsg'] = video_base_info
                info_send['params']['messageContent']['videoMsg']['subjectName'] = video_subjectname
                info_send['params']['messageContent']['videoMsg']['subjectId'] = video_subjectId
                info_send['params']['messageContent']['videoMsg']['moduleNameList'] = video_muduleList
                res4 = req.req(info_send)
                myassert.assert_json(res4)

                view_live_info = apiinfo.getapi('studycontentGet')
                view_live_info['params']['clazzId'] = get_clazzid
                view_live_info['params']['businessId'] = video_base_info['videoId']
                view_live_info['params']['typeEnum'] = 'VIDEO'

                # 查看发送到群里面的录播详情
                res5 = req.req(view_live_info)
                myassert.assert_json(res5)
                myassert.json_key_should_not_equal_specified_value(res5, 'clazzStudyContentVideoCustomerVos', [])

                # 在历史消息中查看发送的消息
                check_json = {'videoId': video_base_info['videoId'], 'videoName': video_base_info['videoName'],
                              'teacherName': video_base_info['teacherName'], 'totalTime': video_base_info['totalTime']}
                myassert.assert_history_msg_c2c(get_studentcid, check_json)

                all_pass = True
                # 只要能成功发送一条消息，则中断循环
                break
            break
        assert all_pass, '该班级下未查询到录播信息'


if __name__ == '__main__':
    pytest.main()
