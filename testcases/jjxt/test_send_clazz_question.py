#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import AllureCaseType, tools
from random import randint, shuffle


@allure.epic('我的班级')
@allure.feature('群聊')
@allure.story("群答题")
@pytest.mark.myclass
@pytest.mark.groupmsg
class TestSendQuestion():

    @pytest.fixture()
    def get_question_id(self, get_goodsid):

        '''
        随机获取一个群答题的试题ID
        :param get_goodsid: 商品id
        :return: 返回试题id
        '''


        # 查询科目信息
        subject_list_info = apiinfo.getapi('subjectList')
        subject_list_info['url'] = apiinfo.modify_url(subject_list_info, goodsId=get_goodsid)
        res = req.req(subject_list_info)
        # 返回的data应该是一个列表，且不能是空
        myassert.assert_json(res)
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
            module_list_info['params']['moduleType'] = 'PAPER'
            res2 = req.req(module_list_info)
            # 查询的模块信息data必须是列表，但是可以是空，为空时跳出循环，查询下一个科目是否为空
            myassert.json_key_should_be_equal_specified_type(res2, 'data', [], log_res_json=True)

            module_data = res2['data']
            # 判断模块是否等于0
            if len(module_data) == 0:
                continue

            # 打乱模块信息，随机获取模块信息
            shuffle(module_data)

            # 遍历打乱顺序的模块信息
            for module in module_data:
                paper_list_info = apiinfo.getapi('paperList')
                paper_list_info['url'] = apiinfo.modify_url(paper_list_info, goodsId=get_goodsid)
                paper_list_info['params']['subjectId'] = subject_id
                paper_list_info['params']['goodsModuleId'] = module['id']

                res3 = req.req(paper_list_info)
                myassert.json_key_should_be_equal_specified_type(res3, 'data', [], log_res_json=True)

                paper_list = res3['data']
                if (len(paper_list)) == 0:
                    continue

                # 打乱所有试卷信息
                shuffle(paper_list)

                # 遍历打乱顺序的试卷
                for paper_info in paper_list:
                    # 查询试卷下的选择题
                    clazz_question_choose_info = apiinfo.getapi('clazzQuestionChoose')
                    clazz_question_choose_info['params']['paperId'] = paper_info['paperId']
                    clazz_question_choose_info['params']['categoryId'] = paper_info['categoryId']
                    clazz_question_choose_info['params']['subjectId'] = subject_id

                    res4 = req.req(clazz_question_choose_info)
                    myassert.json_key_should_be_equal_specified_type(res4, 'data', [], log_res_json=True)

                    # 试卷的试题如果是空的，继续循环查询
                    questions_data = res4['data']
                    if len(questions_data) == 0:
                        continue

                    # 随机选择一道试题
                    questionId = questions_data[randint(0, len(questions_data) - 1)]['examQuestionVo']['questionId']
                    return questionId

        assert False, '该班级下未找到试题信息'

    @allure.title('发送群答题：查询科目-查询模块-查询试卷-查询试题-存题-查询待推题-推送待推题-查询答题详情-历史消息中查看答题信息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    @pytest.mark.repeat(11)
    def test_save_and_push_clazz_question(self, get_customerid, get_clazzid, get_goodsid, get_question_id, get_groupidentifier):
        '''
        发送群答题：查询科目-查询模块-查询试卷-查询试题-存题-查询待推题-推送待推题-查询答题详情-历史消息中查看答题信息
        '''
        save_info = apiinfo.getapi('save')
        save_info['data'][0]['clazzId'] = get_clazzid
        save_info['data'][0]['questionId'] = get_question_id
        save_info['data'][0]['pushDate'] = tools.get_date(h_m_s=False)

        # 存题
        res = req.req(save_info)
        myassert.assert_json(res)

        unpush_info = apiinfo.getapi('unpushed')
        unpush_info['params']['clazzId'] = get_clazzid
        unpush_info['params']['pushDate'] = tools.get_date(h_m_s=False)

        # 查询待推试题
        res2 = req.req(unpush_info)
        myassert.assert_json(res2)
        myassert.json_key_should_not_equal_specified_value(res2, 'clazzQuestionVos', [])
        questions_data = res2['data']['clazzQuestionVos']

        question_data = questions_data[randint(0, len(questions_data) - 1)]
        id = question_data['id']
        # 从待推试题中随机选择一个试题进行推送
        question_id = question_data['examQuestionVo']['questionId']

        # 推题
        push_info = apiinfo.getapi('push')
        push_info['data']['clazzId'] = get_clazzid
        push_info['data']['customerId'] = get_customerid
        push_info['data']['questionId'] = question_id
        push_info['data']['id'] = id
        push_info['data']['pushDate'] = tools.get_date(h_m_s=False)

        res3 = req.req(push_info)
        myassert.assert_json(res3)

        # 查询答题详情
        question_detail = apiinfo.getapi('questionDetail')
        question_detail['params']['clazzQuestionId'] = id

        res4 = req.req(question_detail)
        myassert.assert_json(res4)

        # 在历史消息中查看发送的消息
        check_json = {'questionId': question_id}
        myassert.assert_history_msg(get_groupidentifier, check_json)

    @allure.title('发送群答题：查询科目-查询模块-查询试卷-查询试题-随机存群答题到未来日期')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_save_clazz_question_future(self, get_customerid, get_clazzid, get_goodsid, get_question_id):
        '''
        发送群答题：查询科目-查询模块-查询试卷-查询试题-随机存群答题到未来日期
        '''
        save_info = apiinfo.getapi('save')
        save_info['data'][0]['clazzId'] = get_clazzid
        save_info['data'][0]['questionId'] = get_question_id
        save_info['data'][0]['pushDate'] = tools.get_date(days=3, h_m_s=False)

        # 推送试题
        res = req.req(save_info)
        myassert.assert_json(res)

    @allure.title('发送群答题：查询科目-查询模块-查询试卷-查询试题-随机存群答题到过去日期')
    @allure.severity(AllureCaseType.NORMAL)
    # @pytest.mark.flaky(reruns=5)
    def test_save_clazz_question_formerly(self, get_customerid, get_clazzid, get_goodsid, get_question_id):
        '''
        发送群答题：查询科目-查询模块-查询试卷-查询试题-随机存群答题到过去日期
        '''
        save_info = apiinfo.getapi('save')
        save_info['data'][0]['clazzId'] = get_clazzid
        save_info['data'][0]['questionId'] = get_question_id
        save_info['data'][0]['pushDate'] = tools.get_date(days=-3, h_m_s=False)

        # 推送试题
        res = req.req(save_info)
        myassert.assert_json(res)

    @allure.title('发送群答题：查询科目-查询模块-查询试卷-查询试题-随机发送群答题-历史消息中查看答题信息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_push_clazz_question(self, get_customerid, get_clazzid, get_goodsid, get_question_id, get_groupidentifier):
        '''
        发送群答题：查询科目-查询模块-查询试卷-查询试题-随机发送群答题-历史消息中查看答题信息
        '''
        push_info = apiinfo.getapi('push')
        push_info['data']['clazzId'] = get_clazzid
        push_info['data']['customerId'] = get_customerid
        push_info['data']['questionId'] = get_question_id

        # 推送试题
        res = req.req(push_info)
        myassert.assert_json(res)

        # 在历史消息中查看发送的消息
        check_json = {'questionId': get_question_id}
        myassert.assert_history_msg(get_groupidentifier, check_json)


    @allure.title('发送群答题：查询科目-查询模块-查询试卷-查询试题-再次推送相同试题，不应该推送成功')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_push_clazz_question_repeat(self, get_customerid, get_clazzid, get_goodsid, get_question_id):
        '''
        发送群答题-查询科目-查询模块-查询试卷-查询试题-再次推送相同试题，不应该推送成功
        '''
        push_info = apiinfo.getapi('push')
        push_info['data']['clazzId'] = get_clazzid
        push_info['data']['customerId'] = get_customerid
        push_info['data']['questionId'] = get_question_id

        # 推送试题
        res = req.req(push_info)
        myassert.assert_json(res)

        # 再次推送相同试题，重新获取接口信息
        push_info2 = apiinfo.getapi('push')
        push_info2['data']['clazzId'] = get_clazzid
        push_info2['data']['customerId'] = get_customerid
        push_info2['data']['questionId'] = get_question_id
        push_info['data']['pushDate'] = tools.get_date(h_m_s=False)

        res2 = req.req(push_info2)
        myassert.assert_json(res2, {"code": 5001})


    @allure.title('发送群答题：删除不存在的群推试题')
    @allure.severity(AllureCaseType.NORMAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    # @pytest.mark.repeat(5)
    def test_delete_not_exists_clazz_question(self):
        '''
        发送群答题：删除不存在的群推试题
        '''
        info = apiinfo.getapi('clazzQuestionDelete')
        ret = req.req(info)
        myassert.assert_json(ret)


if __name__ == '__main__':
    pytest.main()
