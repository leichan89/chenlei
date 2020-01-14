#coding=utf-8
import pytest
import os
import time
import shutil
from datetime import datetime
from py._xmlgen import html
from common.log import logger
from common.configer import configer


dir = os.path.dirname(__file__)
allure_dir = dir + os.sep + 'allure'
allure_report = allure_dir + os.sep + 'report'
allure_result = allure_dir + os.sep + 'result'
allure_history = allure_dir + os.sep + 'report' + os.sep + 'history'
allure_result_history = allure_result + os.sep + 'history'
history_bak = allure_dir + os.sep + 'history'

@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    try:
        # 生成pytest-html报告
        cells.insert(2, html.th('Description'))
        cells.insert(3, html.th('Time', class_='sortable time', col='time'))
        cells.pop()

        # 判断allure上次结果记录目录是否存在，存在则拷贝到当前结果目录中去
        if os.path.exists(history_bak):
            if os.listdir(history_bak):
                logger.debug('生成报告前将allure/history目录下的历史文件拷贝到allure/result目录下，便于生成趋势图')
                shutil.copytree(history_bak, allure_result_history)
        # 生成allure报告，包含历史记录，
        cmd = 'allure generate {result} -o {report} --clean'.format(result=allure_result, report=allure_report)
        logger.debug('执行生成报告命令:%s' % cmd)
        logger.debug('开始生成报告，报告路径：%s' % allure_report)
        os.popen(cmd)
    except:
        errmsg = '生成报告异常'
        logger.error(errmsg)

@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    try:
        cells.insert(2, html.td(report.description))
        cells.insert(3, html.td(datetime.utcnow(), class_='col-time'))
        cells.pop()
    except:
        errmsg = '生成报告:table_row异常'
        logger.error(errmsg)

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    try:
        outcome = yield
        report = outcome.get_result()
        report.description = str(item.function.__doc__)
        # 设置编码显示中文
        report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
    except:
        errmsg = '生成报告:makereport异常'
        logger.error(errmsg)


def pytest_configure(config):
    # 设置pytest-html插件生成的测试报告命令行参数中的路径
    if config.getoption('--html'):
        confpath = config.option.htmlpath
        htmlpath = dir + os.sep + 'report' + os.sep + '{time}-{env}-{path}'.format(
            time=time.strftime('%Y-%m-%d', time.localtime()),
            env=configer.configer().get('env', 'env'),
            path=confpath)
        config.option.htmlpath = htmlpath

    # 配置allure测试结果
    result_dir = config.option.allure_report_dir
    if not result_dir:
        result_dir = allure_result
        if os.path.exists(result_dir):
            logger.debug('删除allure目录下result中的文件')
            shutil.rmtree(result_dir)
        config.option.allure_report_dir = result_dir

    # 生成allure报告前清理history数据
    if os.path.exists(history_bak):
        logger.debug('删除allure备份的history文件')
        shutil.rmtree(history_bak)

    # 将上次历史记录拷贝出来，拷贝前备份历史记录的目录应删除
    if os.path.exists(allure_history):
        # 判断报告中的history目录下是否存在数据
        if os.listdir(allure_history):
            # 运行当前测试用例前把上次的结果记录拷贝出来，运行前先删除该目录
            logger.debug('从历史记录allure/report/history目录拷贝到allure/history目录下')
            shutil.copytree(allure_history, history_bak)
