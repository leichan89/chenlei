#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import AllureCaseType, tools


@pytest.mark.myclass
@allure.epic('我的班级')
@allure.feature("班级")
@allure.story("学员列表")
class TestExportPointMonth():


    @allure.title('导出学员列表数据')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_export_excel(self, get_clazzid, get_stageid_and_taskid):
        '''
        导出学员列表数据
        '''
        info = apiinfo.getapi('exportExcel')
        info['params']['clazzId'] = get_clazzid
        info['params']['studyStageId'] = get_stageid_and_taskid[0]
        info['params']['taskId'] = get_stageid_and_taskid[1]
        res = req.req(info)
        assert res, '下载积分文件失败'


if __name__ == '__main__':
    pytest.main()
