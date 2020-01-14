#coding=utf-8
import pytest
import allure
from common.singleton_conf import app_apiinfo, app_req, app_req_ios
from common.custom_assert import myassert
from common.tools import AllureCaseType


@pytest.mark.myclass
@allure.epic('手机接口')
@allure.feature("消息入口")
@allure.story("消息入口1")
class TestShowPopup():


    @allure.title('显示弹出窗口信息—安卓')
    @allure.severity(AllureCaseType.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=5)
    def test_show_popup_andriod(self):
        '''
        显示信息
        '''
        info = app_apiinfo.getapi('showPopup')
        ret = app_req.req(info)
        myassert.app_assert_json(ret)


    @allure.title('显示弹出窗口信息—IOS')
    @allure.severity(AllureCaseType.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=5)
    def test_show_popup_ios(self):
        '''
        显示信息
        '''
        info = app_apiinfo.getapi('showPopup')
        ret = app_req_ios.req(info)
        myassert.app_assert_json(ret)



if __name__ == '__main__':
    pytest.main()
