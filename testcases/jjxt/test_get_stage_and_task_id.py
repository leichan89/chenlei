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
class TestGetStageAndTaskByClazzId():


    @allure.title('获取阶段和任务id')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=5)
    def test_get_stage_task_id(self, get_stageid_and_taskid):
        '''
        下载积分：设置年月日下载
        '''
        # info = apiinfo.getapi('exportPointMonth')
        # info['params']['clazzId'] = get_clazzid
        # info['params']['startTime'] = tools.get_date(days=-100, h_m_s=False)
        # info['params']['endTime'] = tools.get_date(h_m_s=False)
        # res = req.req(info)
        # assert res, '下载积分文件失败'

        t = get_stageid_and_taskid
        print(t)


if __name__ == '__main__':
    pytest.main()
