#coding=utf-8
import json
import os
from contextlib import closing
from common.configer import configer
from common.session import GetSession, GetAppSession
from common.log import logger
from common.cunstom_exception import ResponseError, ParamsError
from common.tools import tools
# from common.getsig import sig
from urllib.parse import urlencode, unquote

# merge test

class Requests():

    def __init__(self, session_type='jjxt'):
        self.cfg = configer.configer()
        if session_type == 'jjxt':
            self.session = GetSession().session()
            self.endpoint = self.cfg.get('env', 'endpoint')
        # elif session_type == 'andriod':
        #     self.ios = False
        #     self.session = GetAppSession().appsession()
        #     self.sig = sig
        #     self.endpoint = self.cfg.get('app', 'endpoint')
        #     self.default_params = self.get_default_app_params()
        # elif session_type == 'ios':
        #     self.ios = True
        #     self.session = GetAppSession().appsession()
        #     self.sig = sig
        #     self.endpoint = self.cfg.get('app', 'endpoint')
        #     self.default_params = self.get_default_app_params_ios()
        else:
            errmsg = '初始化session失败，无效的参数:【%s】' % session_type
            logger.error(errmsg)
            assert False, errmsg

    def req(self, info, status_code=200, url_userdefine=False, **kw):
        if info:
            logger.info('\n\n' + format('接口请求分割线', '*^157s') + '\n')
            logger.info('开始访问接口:【{apiname}:{api_description}】'.format(
                apiname=info['name'],
                api_description=info['api_description'])
            )
            self._diff_keys(info)
            method = info['method'].lower()
            url = info['url']
            headers = info['headers']
            if headers:
                logger.info('请求的headers信息为\n%s' % tools.format_json(headers))
            if not url_userdefine:
                info['url'] = self.endpoint + url
            try:
                if method == 'get':
                    ret = self._get(info, **kw)
                    return self._get_response(ret, status_code=status_code)
                elif method == 'post':
                    ret = self._post(info, **kw)
                    return self._get_response(ret, status_code=status_code)
                elif method == 'post_form':
                    ret = self._form(info, **kw)
                    return self._get_response(ret, status_code=status_code)
                elif method == 'post_export_file':
                    self._export_file(info)
                    return True
                elif method == 'app_post':
                    ret = self._post_app(info, **kw)
                    return self._get_response(ret, status_code=status_code)
                elif method == 'app_get':
                    ret = self._get_app(info, **kw)
                    return self._get_response(ret, status_code=status_code)
                else:
                    errmsg = '请求的方法不存在，请检查excel中是否填写正确，支持get、post、post_form、post_export_file'
                    logger.error(errmsg)
            except ResponseError as err:
                errmsg = err
            except ParamsError as err:
                errmsg = err
            except Exception as err:
                if str(err).find('Failed to establish a new connection') != -1:
                    errmsg = '访问接口失败，未能建立连接，请检查接口地址或网络环境是否OK'
                    logger.error(errmsg)
                else:
                    errmsg = '接口请求发生未知异常, %s' % err
                    logger.error(errmsg)
        else:
            errmsg = '接口信息为空'
            logger.error(errmsg)
        if errmsg:
            assert False, errmsg


    def _post(self, info, **kw):
        logger.info('发送post请求')
        data = info['data']
        try:
            logger.info('请求参数信息为\n%s' % tools.format_json(data))
            # 将字典转换为json格式的字符串，会自动替换字典中的None、True、False为null、true、false
            # 如果不转换为字符串，上传文件接口会报错：Object of type MultipartEncoder is not JSON serializable

            data = json.dumps(data)
        except:
            logger.debug('将json转换为字符失败')
        ret = self.session.post(url=info['url'], headers=info['headers'], data=data, **kw)
        return ret

    # 另外一种post方式
    # def _post(self, info, **kw):
    #     logger.info('发送post请求')
    #     data = info['data']
    #     ret = self.session.post(url=info['url'], headers=info['headers'], json=data, **kw)
    #     return ret

    def _form(self, info, **kw):
        logger.info('发送post_form请求')
        params = info['params']
        if params:
            if isinstance(params, dict):
                logger.info('请求参数信息为\n%s' % tools.format_json(params))
                # 将字典参数转换为query参数，需要替换字典中的None、True、False为null、true、false
                params = urlencode(self._format_json_data(info['params']))
            else:
                errmsg = "post_form请求的参数必须是字典类型或者为空"
                logger.error(errmsg)
                raise ParamsError(errmsg)
        ret = self.session.post(url=info['url'], headers=info['headers'], params=params, **kw)
        return ret


    def _get(self, info, **kw):
        # 传入一个字典参数
        logger.info('发送get请求')
        params = info['params']
        if params:
            if isinstance(params, dict):
                logger.info('请求参数信息为\n%s' % tools.format_json(params))
                # params = self._format_json_data(info['params'])
            else:
                errmsg = "get请求的参数必须是字典类型或者为空"
                logger.error(errmsg)
                raise ParamsError(errmsg)
        ret = self.session.get(url=info['url'], headers=info['headers'], params=params, **kw)
        return ret

    def _export_file(self, info):
        logger.info('发送导出文件get请求')
        params = info['params']
        if isinstance(params, dict):
            logger.info('请求参数信息为\n%s' % tools.format_json(params))
            with closing(self.session.get(url=info['url'], headers=info['headers'], params=info['params'],
                                                stream=True)) as res:
                if res:
                    res_headers = res.headers
                    try:
                        filename = res_headers['Content-disposition'].split(';')[-1].split('=')[-1]
                        filename = unquote(filename)
                    except:
                        errmsg = '接口响应头信息中未获取到文件名称，%s' % res.json()
                        logger.error(errmsg)
                        raise ResponseError(errmsg)
                    file_path = os.path.dirname(os.path.dirname(__file__)) + os.sep + 'temp' + os.sep + filename
                    with open(file_path, 'wb') as fb:
                        # 每次最多接受1k
                        for chunk in res.iter_content(chunk_size=1024):
                            if chunk and type(chunk) == bytes:
                                fb.write(chunk)
                    if not os.path.exists(file_path):
                        errmsg = '下载文件失败'
                        logger.error(errmsg)
                        raise ResponseError(errmsg)
                    else:
                        logger.info('文件【%s】下载完成' % filename)
                        fileinfo = os.stat(file_path)
                        logger.debug('文件大小为：%s' % fileinfo.st_size)
                        os.remove(file_path)
                        logger.debug('删除下载的文件')
                else:
                    errmsg = '下载接口响应异常'
                    logger.error(errmsg)
                    raise ResponseError(errmsg)
        else:
            errmsg = "get请求的参数必须是字典类型"
            logger.error(errmsg)
            raise ParamsError(errmsg)


    def _post_app(self, info, **kw):
        logger.info('发送app端post请求')
        params = info['params']
        data = info['data']
        if params:
            if not isinstance(params, dict):
                errmsg = "post_app请求的params参数必须是字典类型或者为空"
                logger.error(errmsg)
                raise ParamsError(errmsg)
            # 拼接参数
            params = dict(self.default_params, **params)
        else:
            params = self.default_params
        logger.info('请求params参数信息为\n%s' % tools.format_json(params))
        if data:
            if not isinstance(data, dict):
                errmsg = "post_app请求的data参数必须是字典类型或者为空"
                logger.error(errmsg)
                raise ParamsError(errmsg)
            logger.info('请求body参数信息为\n%s' % tools.format_json(data))
        url = self.sig.get_url_include_sig(info['url'] + '?' + urlencode(params), ios=self.ios)
        ret = self.session.post(url=url, headers=info['headers'], json=data, **kw)
        return ret

    def _get_app(self, info, **kw):
        logger.info('发送app端get请求')
        params = info['params']
        if params:
            if not isinstance(params, dict):
                errmsg = "get_app请求的params参数必须是字典类型或者为空"
                logger.error(errmsg)
                raise ParamsError(errmsg)
            # 拼接参数
            params = dict(self.default_params, **params)
        else:
            params = self.default_params
        logger.info('请求params参数信息为\n%s' % tools.format_json(params))
        url = self.sig.get_url_include_sig(info['url'] + '?' + urlencode(params), ios=self.ios)
        ret = self.session.get(url=url, headers=info['headers'], **kw)
        return ret

    # 目的是为了当发送请求时，如果修改params中的参数为None、True、False，则需要将其转换为null、true、false
    def _format_json_data(self, data):
        temp_data = data
        for k, v in temp_data.items():
            if isinstance(v, dict):
                self._format_json_data(v)
            else:
                if isinstance(v, bool) or v is None:
                    v = str(v)
                    v = v.replace('\'', '\"').replace('None', 'null').replace('False', 'false').replace('True', 'true')
                    temp_data[k] = v
                else:
                    temp_data[k] = v
        return temp_data

    def _get_response(self, ret, status_code=None):
        logger.info('接口请求地址为\n%s' % ret.url)
        try:
            code = ret.status_code
            if code == status_code:
                logger.info('响应状态码为:{code}，响应时间为:{time}'.format(code=status_code,
                                                                time=ret.elapsed.total_seconds()))
                try:
                    return ret.json()
                except:
                    logger.info('响应信息不为json')
                    return ret
            else:
                errmsg = '接口响应状态码错误：%s' % code
                logger.error(errmsg)
        except Exception:
            errmsg = '接口响应异常：%s' % ret
            logger.error(errmsg)
        if errmsg:
            raise ResponseError(errmsg)


    def _diff_keys(self, info):
        keys = ['name', 'api_description', 'method', 'headers', 'url', 'params', 'data']
        info_keys = info.keys()
        # 不存在的key
        diff_keys = [key for key in info_keys if key not in keys]
        if diff_keys:
            errmsg = '接口info中传入的参数名称错误:%s' % diff_keys
            logger.error(errmsg)
            logger.info('接口info中应传入的参数名称有：%s' % keys)
            assert False, errmsg
        else:
            # 未传入的key
            diff_keys2 = [key for key in keys if key not in info_keys]
            if diff_keys2:
                errmsg = '接口info中存在未传入的参数：%s' % diff_keys2
                logger.error(errmsg)
                assert False, errmsg

    def get_default_app_params(self):
        default_params = {}
        default_params['userName'] = self.cfg.get('andriod', 'userName')
        default_params['password'] = self.cfg.get('andriod', 'password')
        default_params['app_key'] = self.cfg.get('andriod', 'app_key')
        default_params['device'] = self.cfg.get('andriod', 'device')
        default_params['kernel'] = self.cfg.get('andriod', 'kernel')
        default_params['rom'] = self.cfg.get('andriod', 'rom')
        default_params['sk'] = self.cfg.get('andriod', 'sk')
        default_params['token'] = self.cfg.get('andriod', 'token')
        default_params['v'] = self.cfg.get('andriod', 'v')
        default_params['app_version'] = self.cfg.get('andriod', 'app_version')
        default_params['device_type'] = self.cfg.get('andriod', 'device_type')
        params = urlencode(default_params)
        url = self.cfg.get('app', 'loginurl') + '?' + params
        try:
            url = self.sig.get_url_include_sig(url)
            logger.debug('andriod登陆链接为：\n%s' % url)
            logger.debug('开始登陆app，用户名为：%s' % default_params['userName'])
            ret = self.session.post(url=url)
            del default_params['userName']
            del default_params['password']
            default_params['sk'] = ret.json()['data'][0]['sk']
            return default_params
        except:
            errmsg = '登陆app失败'
            logger.error(errmsg)
            assert False, errmsg


    def get_default_app_params_ios(self):
        default_params = {}
        default_params['userName'] = self.cfg.get('ios', 'userName')
        default_params['password'] = self.cfg.get('ios', 'password')
        default_params['app_key'] = self.cfg.get('ios', 'app_key')
        default_params['device'] = self.cfg.get('ios', 'device')
        default_params['kernel'] = self.cfg.get('ios', 'kernel')
        default_params['rom'] = self.cfg.get('ios', 'rom')
        default_params['token'] = self.cfg.get('ios', 'token')
        default_params['v'] = self.cfg.get('ios', 'v')
        default_params['app_version'] = self.cfg.get('ios', 'app_version')
        params = urlencode(default_params)
        url = self.cfg.get('app', 'loginurl') + '?' + params
        try:
            url = self.sig.get_url_include_sig(url, ios=True)
            logger.debug('IOS登陆链接为：\n%s' % url)
            logger.debug('开始登陆app，用户名为：%s' % default_params['userName'])
            ret = self.session.post(url=url)
            del default_params['userName']
            del default_params['password']
            default_params['sk'] = ret.json()['data'][0]['sk']
            return default_params
        except:
            errmsg = '登陆app失败'
            logger.error(errmsg)
            assert False, errmsg

if __name__ == '__main__':
    pass
