#coding=utf-8
import pytest
import allure
from common.singleton_conf import app_apiinfo, app_req
from common.custom_assert import myassert
from common.tools import AllureCaseType


@pytest.mark.myclass
@allure.epic('手机接口')
@allure.feature("消息入口")
@allure.story("消息入口1")
class TestGetAllGroupMember():


    @allure.title('获取所有组成员信息')
    @allure.severity(AllureCaseType.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=5)
    def test_get_all_group_member(self):
        '''
        获取所有组成员信息
        '''
        info = app_apiinfo.getapi('getAllGroupMember')
        ret = app_req.req(info)
        myassert.app_assert_json(ret)



if __name__ == '__main__':
    pytest.main()
