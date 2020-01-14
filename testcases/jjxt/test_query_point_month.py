#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import AllureCaseType, tools


@pytest.mark.myclass
@allure.epic('我的班级')
@allure.feature("班级")
@allure.story("积分")
class TestQueryPointMonthByPage():


    @allure.title('查询积分：默认查询')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_default_query(self):
        '''
        查询积分：默认查询
        '''
        info = apiinfo.getapi('queryPointMonthByPage')
        res = req.req(info)
        myassert.assert_json(res)


    @allure.title('查询积分：指定时间段查询')
    @allure.severity(AllureCaseType.NORMAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_given_time_query(self):
        '''
        查询积分：指定时间段查询
        '''
        info = apiinfo.getapi('queryPointMonthByPage')
        info['params']['startTime'] = tools.get_date(days=-200, h_m_s=False)
        info['params']['endTime'] = tools.get_date(h_m_s=False)
        res = req.req(info)
        myassert.assert_json(res)


    @allure.title('查询积分：开始时间大于结束时间')
    @allure.severity(AllureCaseType.MINOR)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_given_time_query_starttime_gt_endtime(self):
        '''
        查询积分：开始时间大于结束时间
        '''
        info = apiinfo.getapi('queryPointMonthByPage')
        info['params']['startTime'] = tools.get_date(h_m_s=False)
        info['params']['endTime'] = tools.get_date(days=-200, h_m_s=False)
        res = req.req(info)
        myassert.assert_json(res)


if __name__ == '__main__':
    pytest.main()
