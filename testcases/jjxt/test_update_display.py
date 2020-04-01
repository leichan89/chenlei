#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import AllureCaseType, tools


@pytest.mark.myclass
@allure.epic('我的班级')
@allure.feature("群聊")
@allure.story("设置群答题显示解析")
class TestUpdataDisplay:


    @allure.title('设置群答题显示解析为手动')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_update_display(self, get_clazzid):
        '''
        设置群答题显示解析为手动
        '''
        info = apiinfo.getapi('updateDisplay')
        info['params']['clazzId'] = get_clazzid
        res = req.req(info)
        myassert.assert_json(res)


if __name__ == '__main__':
    pytest.main()
