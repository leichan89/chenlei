#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.tools import AllureCaseType



@allure.epic('学员管理')
@allure.feature('学员管理')
@allure.story("导出")
@pytest.mark.myclass
class TestExportStudent():

    @allure.title('导出基本信息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.flaky(reruns=5)
    def test_exportStudent(self):
        '''
        导出基本信息
        '''
        info = apiinfo.getapi('exportStudent')
        res = req.req(info)
        assert res, '下载学员信息失败'



if __name__ == '__main__':
    pytest.main()
