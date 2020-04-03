
#coding=utf-8

import pytest
from common.custom_assert import myassert
from common.configer import GetConfiger
from common.log import logger
from random import randint

@pytest.fixture(scope='session')
def get_customerid():
    '''
    获取老师id
    :return:老师id
    '''

    from common.singleton_conf import apiinfo, req
    # 查询老师信息id
    loginuser_info = apiinfo.getapi('loginUser')
    res = req.req(loginuser_info)
    myassert.assert_json(res)
    myassert.json_key_should_not_equal_specified_value(res, 'data', {})
    userId = res['data']['id']
    # 获取老师id
    teacher_info = apiinfo.getapi('findByUserId')
    teacher_info['url'] = apiinfo.modify_url(teacher_info, userId=userId)
    res2 = req.req(teacher_info)
    myassert.assert_json(res2)
    myassert.json_key_should_not_equal_specified_value(res, 'data', {})
    teacher_id = res2['data']['id']
    return teacher_id


@pytest.fixture(scope='session')
def get_clazzinfo(get_customerid):
    from common.singleton_conf import apiinfo, req
    '''
    获取班级id
    :param get_teacherid:老师id
    :return:返回配置文件中配置的班级的id
    '''

    configer = GetConfiger()
    clazzname = configer.configer().get('env', 'clazzname')
    clazzid_info = apiinfo.getapi('forChat')
    clazzid_info['params']['teacherId'] = get_customerid
    res = req.req(clazzid_info)
    myassert.assert_json(res)
    myassert.json_key_should_not_equal_specified_value(res, 'data', {})
    data = res['data']['officalClazzs']
    for d in data:
        if d['clazzName'] == clazzname:
            return d
    errmsg = '获取班级【%s】的id失败' % clazzname
    logger.error(errmsg)
    assert False, errmsg


@pytest.fixture(scope='session')
def get_clazztypeid(get_clazzinfo):
    return get_clazzinfo['clazzTypeId']


@pytest.fixture(scope='session')
def get_clazzid(get_clazzinfo):
    return get_clazzinfo['clazzId']


@pytest.fixture(scope='session')
def get_goodsid(get_clazzinfo):
    return get_clazzinfo['goodsId']


@pytest.fixture(scope='session')
def get_groupidentifier(get_clazzinfo):
    return get_clazzinfo['groupIdentifier']


@pytest.fixture(scope='session')
def get_studentid(get_clazzid):
    '''
    获取配置文件中指定手机号码的学员的id
    :param get_clazzid:
    :return:
    '''

    from common.singleton_conf import apiinfo, req
    configer = GetConfiger()
    clazzname = configer.configer().get('env', 'clazzname')
    student_mobile = configer.configer().get('env', 'student_mobile')
    student_list_info = apiinfo.getapi('student-list')
    student_list_info['params']['clazzId'] = get_clazzid
    res = req.req(student_list_info)
    myassert.assert_json(res)
    myassert.json_key_should_not_equal_specified_value(res, 'data', {})
    data = res['data']['students']['items']
    for d in data:
        if d['mobile'] == student_mobile:
            return d['customerId']
    errmsg = '获取【{clazzname}】下的手机号码为【{mobile}】的学员id失败'.format(clazzname=clazzname, mobile=student_mobile)
    logger.error(errmsg)
    assert False, errmsg


@pytest.fixture(scope='session')
def get_studentcid(get_studentid):
    '''
    获取配置文件中指定手机号码的学员的腾讯账号
    :param get_studentid: 学员id
    :return:
    '''
    return 'C-%s' % str(get_studentid)


@pytest.fixture(scope='session')
def get_stageid_and_taskid(get_clazzid):
    '''
    获取指定班级的某个任务和id
    :param get_clazzid:班级id
    :return:随机的阶段id和任务id
    '''
    from common.singleton_conf import apiinfo, req
    info = apiinfo.getapi('getStageAndTaskByClazzId')
    info['params']['clazzId'] = get_clazzid
    res = req.req(info)
    myassert.assert_json(res)
    myassert.json_key_should_not_equal_specified_value(res, 'data', [])
    data = res['data']
    s_t_data = data[randint(0, len(data) -1)]
    try:
        clazzStudyTaskVos = s_t_data['clazzStudyTaskVos']
        len_study_stask = len(clazzStudyTaskVos)
        s_t = clazzStudyTaskVos[randint(0, len_study_stask - 1)]
    except:
        errmsg = '获取阶段id和任务id失败'
        logger.error(errmsg)
        assert False, errmsg
    stageId = s_t['stageId']
    taskId = s_t['taskId']
    return stageId, taskId

