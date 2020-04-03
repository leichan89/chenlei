# coding=utf-8

from common.apiinfo import ApiInfo
from common.myrequests import Requests


# 读取apiinfo.xlsx文件中class这个sheet
apiinfo = ApiInfo()

# 读取apiinfo.xlsx文件中app这个sheet
app_apiinfo = ApiInfo(sheet_name='app')


# 精进后台接口请求
req = Requests()

# # andriod接口请求实例
app_req = Requests('andriod')

# ios接口请求实例
app_req_ios = Requests('ios')

