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
class TestExportPointMonth():


    @allure.title('下载积分：设置年月日下载')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_has_date_export(self, get_clazzid):
        '''
        下载积分：设置年月日下载
        '''
        info = apiinfo.getapi('exportPointMonth')
        info['params']['clazzId'] = get_clazzid
        info['params']['startTime'] = tools.get_date(days=-100, h_m_s=False)
        info['params']['endTime'] = tools.get_date(h_m_s=False)
        res = req.req(info)
        assert res, '下载积分文件失败'


    @allure.title('下载积分：不带年月日下载')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_default_export(self, get_clazzid):
        '''
        下载积分：不带年月日下载
        '''
        info = apiinfo.getapi('exportPointMonth')
        info['params']['clazzId'] = get_clazzid
        info['params']['startTime'] = ''
        info['params']['endTime'] = ''
        res = req.req(info)
        assert res, '下载积分文件失败'


if __name__ == '__main__':
    pytest.main()
