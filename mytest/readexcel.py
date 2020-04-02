# coding=utf-8

import os
import pandas as pd
from common.log import logger


'''
Q:为什么要用excel存储接口信息？
A:因为接口数量相对较少，方便修改接口信息，查看方便

读取excel步骤：
1、通过excel路径（也可以指定sheet名称）读取所有数据
2、通过查找指定列中的字符来获取到指定字符所在行的一整行数据
3、解析获取到多行数据
4、拼接数据

'''

class ApiInfo():


    def __init__(self, filename='test.xlsx', sheet_name='class'):
        self.sheet_name = sheet_name
        self.filename = filename
        errmsg = ''
        try:

            # 拼接指定excel文件的绝对路径
            xlsx_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'apiinfo' + os.sep + self.filename

            # 设置显示的最大行数和列数
            pd.set_option('display.max_rows', 1000, 'display.max_columns', 1000, "display.max_colwidth", 1000,
                          'display.width', 1000)

            # 指定sheet名称读取excel内容
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
            # 获取指定列中，值为指定字符时，该行的整行数据，包括每一列的名称
            api = self.xlsx[self.xlsx['name'] == apiname]
            print(api)
            apiname = self._replace_nan(api['name'])
            if apiname:
                # 或者指定列的值
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
                # 获取指定列的值，可能会出现多个，这里取第一个
                value = value.values[0]
            except:
                errmsg = '在excel列【%s】中查找信息无返回数据' % value.name
                logger.error(errmsg)
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




if __name__ == '__main__':
    api = ApiInfo()
    print(api.getapi('LOG'))
