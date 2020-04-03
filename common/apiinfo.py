# coding=utf-8

import os
import re
import json
import pandas as pd
from common.log import logger
from requests_toolbelt import MultipartEncoder
from common.tools import tools
from common.cunstom_exception import IndexOutOfBoundsError, ParamsError, ExcelParamIsEmptyError


class ApiInfo():


    def __init__(self, filename='apiinfo.xlsx', sheet_name='class'):
        self.sheet_name = sheet_name
        self.filename = filename
        errmsg = ''
        try:
            xlsx_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'apiinfo' + os.sep + self.filename
            pd.set_option('display.max_rows', 1000, 'display.max_columns', 1000, "display.max_colwidth", 1000,
                          'display.width', 1000)
            self.xlsx = pd.read_excel(xlsx_path, sheet_name=sheet_name)
        except FileNotFoundError:
            errmsg = '打开excel【%s】异常，找不到excel文件' % self.filename
            logger.error(errmsg)
        except Exception as err:
            errmsg = '打开excel【{filename}】异常\n{err}'.format(filename=filename, err=err)
            logger.error(errmsg)
        finally:
            if errmsg:
                assert False, errmsg

    def getapi(self, apiname):
        info = {}
        errmsg = ''
        try:
            api = self.xlsx[self.xlsx['name'] == apiname]
            apiname = self._replace_nan(api['name'])
            if apiname:
                info['name'] = apiname
                info['api_description'] = self._replace_nan(api['api_description'])
                info['method'] = self._replace_nan(api['method'])
                info['url'] = self._replace_nan(api['url'])
                # 以上信息为必填信息，不能为空
                for k, v in info.items():
                    if v is None:
                        errmsg = '获取接口【{apiname}】信息异常，在excel中接口的【{name}】信息为必填信息'.format(
                            apiname=apiname, name=k)
                        logger.error(errmsg)
                        raise ExcelParamIsEmptyError(errmsg)

                api_base_err_info = '获取接口【{apiname}:{api_description}】信息异常，'.format(
                    apiname=apiname,
                    api_description=info['api_description']
                )
                # headers必须是一个字典或者为None
                headers = self._replace_nan(api['headers'])
                if headers:
                    try:
                        # 将excel中的字符转换成json格式，转换前需要将单引号替换为双引号
                        headers = json.loads(headers.replace('\'', '\"'))
                        if not isinstance(headers, dict):
                            errmsg = '{api_base_err_info}info的headers格式有误，必须是一个json格式:\n{headers}'.format(
                                api_base_err_info=api_base_err_info, headers=headers)
                            logger.error(errmsg)
                            raise ParamsError(errmsg)
                    except:
                        errmsg = '{api_base_err_info}info的headers数据有误，转换为json时出错:\n{headers}'.format(
                                api_base_err_info=api_base_err_info, headers=headers)
                        logger.error(errmsg)
                        raise ParamsError(errmsg)
                else:
                    logger.debug('%sinfo中接口的headers为空' % api_base_err_info)
                info['headers'] = headers

                # params必须是一个字典或者为None
                params = self._replace_nan(api['params'])
                if params:
                    try:
                        params = json.loads(params.replace('\'', '\"'))
                        if not isinstance(params, dict):
                            errmsg = '{api_base_err_info}info的params格式有误，必须是一个json格式:\n{params}'.format(
                                api_base_err_info=api_base_err_info, params=params)
                            logger.error(errmsg)
                            raise ParamsError(errmsg)
                    except:
                        errmsg = '{api_base_err_info}info的params数据有误，转换为json时出错:\n{params}'.format(
                                api_base_err_info=api_base_err_info, params=params)
                        logger.error(errmsg)
                        raise ParamsError(errmsg)
                else:
                    logger.debug('%sinfo中接口的params为空' % api_base_err_info)
                info['params'] = params

                # data格式可以是字典也可以是其他类型或者为None
                data = self._replace_nan(api['data'])
                if data:
                    try:
                        data = json.loads(data.replace('\'', '\"'))
                    except:
                        errmsg = ('{api_base_err_info}接口的data数据有误，转换为json时出错:\n{data}'.format(
                                api_base_err_info=api_base_err_info, data=data))
                        logger.error(errmsg)
                        raise ParamsError(errmsg)
                else:
                    logger.debug('%sinfo中接口的data为空' % api_base_err_info)
                info['data'] = data
            else:
                errmsg = 'excel中未找到接口【%s】的信息' % apiname
                logger.error(errmsg)
        except IndexOutOfBoundsError as err:
            errmsg = err
        except ExcelParamIsEmptyError as err:
            errmsg = err
        except ParamsError as err:
            errmsg = err
        except KeyError:
            errmsg = '获取接口【%s】信息异常，excel列名称错误' % apiname
            logger.error(errmsg)
        except TypeError as err:
            errmsg = '获取接口【{apiname}】信息异常，\n{err}'.format(apiname=apiname, err=err)
            logger.error(errmsg)
        except Exception as err:
            errmsg = '获取接口【{apiname}】信息异常\n{err}'.format(apiname=apiname, err=err)
            logger.error(errmsg)
        finally:
            if errmsg:
                assert False, errmsg
            else:
                return info

    def _replace_nan(self, value):
        if isinstance(value, pd.core.series.Series):
            try:
                value = value.values[0]
            except:
                errmsg = '在excel列【%s】中查找信息无返回数据' % value.name
                logger.error(errmsg)
                raise IndexOutOfBoundsError(errmsg)
            if not isinstance(value, str):
                value = str(value)
                if value == 'nan':
                    value = None
            else:
                value = value.strip()
            if value == 'None':
                value = None
            return value
        else:
            raise TypeError('传入的参数类型错误，不是Series类型数据，%s' % value)


    def modify_url(self, info, **kw):
        apiname = info['name']
        api_description = info['api_description']
        url = info['url']
        api_base_err_info = '接口【%s:%s】' % (apiname, api_description)
        try:
            if url:
                url_params = re.findall('{.*?}', url)
                if url_params:
                    url_params = [param.strip('{').strip('}') for param in url_params]
                    try:
                        keys = kw.keys()
                        diff_url_params = [param for param in keys if param not in url_params]
                        if diff_url_params:
                            err_param = '{api_base_err_info}传入的url参数存在错误，错误参数为:{diff_url_params}'.format(
                                api_base_err_info=api_base_err_info,
                                diff_url_params=diff_url_params
                            )
                            raise ParamsError(err_param)
                        else:
                            diff_url_params2 = [param for param in url_params if param not in keys]
                            if diff_url_params2:
                                err_param2 = '{api_base_err_info}传入url中的参数不完整，未传入的参数为:{diff_url_params2}'.format(
                                    api_base_err_info=api_base_err_info,
                                    diff_url_params2=diff_url_params2
                                )
                                raise ParamsError(err_param2)
                            else:
                                for key, value in kw.items():
                                    param = '{%s}' % key
                                    if isinstance(value, int):
                                        value = str(value)
                                    url = url.replace(param, value)
                                return url
                    except ParamsError as err:
                        errmsg = err
                        logger.error(errmsg)
                        logger.info('{api_base_err_info}中的url中应传入的参数名称有:'
                                     '{url_params}'.format(api_base_err_info=api_base_err_info, url_params=url_params))
                    except Exception as err:
                        errmsg = '{api_base_err_info}修改url中的参数发生异常\n{err}'.format(
                            api_base_err_info=api_base_err_info, err=err)
                        logger.error(errmsg)
                else:
                    errmsg = '{api_base_err_info}的url中不存在参数信息:{url}'.format(
                        api_base_err_info=api_base_err_info, url=url)
                    logger.error(errmsg)
            else:
                errmsg = '%s的url为空' % api_base_err_info
                logger.error(errmsg)
        except Exception as err:
            errmsg = '{api_base_err_info}获取url信息失败，接口信息无url信息\n{err}'.format(
                api_base_err_info=api_base_err_info, err=err)
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg


    def get_upload_temp_file_info(self, info, filename):
        filepath = tools.get_temp_path(filename)
        filetype = tools.get_file_mimetype(filepath)
        file = {'file': (filename, open(filepath, 'rb'), filetype)}
        m = MultipartEncoder(file)
        info['data'] = m
        info['headers'] = {'Content-Type': m.content_type}
        return info



if __name__ == '__main__':
    api = ApiInfo()
    ps = api.getapi('clazzQuestionChoose')['params']
    print(ps)
