#coding=utf-8
import pytest
from common.singleton_conf import apiinfo, req
from common.tools import tools
from common.custom_assert import myassert


def return_url_params():
    url_params = []
    for i in [1000, 2000, 3000, 4000]:
        params = {'teacherId': i}
        url_params.append(params)
    return url_params


@pytest.fixture(params=return_url_params())
def url_params(request):
    return request.param


@pytest.fixture()
def get_history_msg(get_groupidentifier):
    '''
    获取群聊中的历史消息
    :param get_groupidentifier:
    :return: 最近一天的历史消息
    '''
    history_msg_info = apiinfo.getapi('historyMsg')
    history_msg_info['params']['groupIdentifier'] = get_groupidentifier
    history_msg_info['params']['startDate'] = tools.get_date(days=-1)
    history_msg_info['params']['endDate'] = tools.get_date()
    res = req.req(history_msg_info)
    myassert.assert_json(res)


