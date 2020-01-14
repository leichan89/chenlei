#coding=utf-8
import pytest
import allure
from common.singleton_conf import apiinfo, req
from common.custom_assert import myassert
from common.tools import AllureCaseType


@allure.epic('我的班级')
@allure.feature('班级')
@allure.story("查询老师信息")
@pytest.mark.myclass
class TestGetTeacherImInfo():

    @pytest.fixture()
    def teacher_im_info(self):
        info = apiinfo.getapi('getTeacherImInfo')
        return info

    @allure.title('查询存在的老师信息')
    @allure.severity(AllureCaseType.CRITICAL)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=3)
    def test_get_teacher_im_info(self,teacher_im_info, get_customerid):
        '''
        查询存在的老师信息
        '''
        teacher_im_info['url'] = apiinfo.modify_url(teacher_im_info, teacherId=get_customerid)
        res = req.req(teacher_im_info)
        myassert.assert_json(res)

    @allure.title('传入无效的字符查询老师信息')
    @allure.severity(AllureCaseType.MINOR)
    @pytest.mark.smoke
    # @pytest.mark.flaky(reruns=3)
    def test_get_teacher_im_info_invalid_param(self, teacher_im_info, url_params):
        '''
        传入无效的字符查询老师信息
        '''
        teacher_im_info['url'] = apiinfo.modify_url(teacher_im_info, **url_params)
        res = req.req(teacher_im_info)
        myassert.assert_json(res, {'code': 500})



if __name__ == '__main__':
    pytest.main()
