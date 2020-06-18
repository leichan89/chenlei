from urllib.parse import urlencode
import requests
from random import randint
from functools import partial
from common.configer import GetConfiger
from common.session import StudySession
from common.tools import tools
from common.log import logger


class InsertCK:


    def __init__(self, user_id):
        configer = GetConfiger()
        cfg = configer.configer()
        self._endpoint = cfg.get('env', 'endpoint_study')
        self._ck_endpoint = cfg.get('env', 'ck_endpoint')
        self._session = StudySession().session()
        self._user_id = user_id

    # 获取直播的信息，类别、科目、id信息
    def _get_live_info_type0(self, keyword, verify_name, page):
        live_info = []
        if keyword:
            params = {"page": 1, "size": page * 100, "keyword": keyword}
        else:
            params = {"page": 1, "size": page * 100}
        rst = self._session.get(url=f'{self._endpoint}/live/page', params=params)
        try:
            items = rst.json()['data']['items']
        except:
            errmsg = '获取直播信息失败，登陆或者接口请求失败'
            raise Exception(errmsg)
        if items:
            for item in items:
                livename = item['liveName']
                if verify_name:
                    if livename == keyword:
                        media_id = item['id']
                        categoryId = item['categoryId']
                        subjectId = item['subjectId']
                        live_info.append([media_id, categoryId, subjectId])
                else:
                    media_id = item['id']
                    categoryId = item['categoryId']
                    subjectId = item['subjectId']
                    live_info.append([media_id, categoryId, subjectId])
        if live_info:
            return live_info
        else:
            errmsg = '获取到的直播信息为空'
            raise Exception(errmsg)

    # 获取直播的信息，类别、科目、id信息
    def _get_video_info_type2(self, keyword, verify_name, page):
        videos_info = []
        if keyword:
            params = {"page": 1, "size": page * 100, "keyword": keyword}
        else:
            params = {"page": 1, "size": page * 100}
        try:
            rst = self._session.get(url=f'{self._endpoint}/video/page', params=params)
            items = rst.json()['data']['items']
        except:
            raise Exception('获取直播列表信息异常，登陆或者接口请求失败')
        if items:
            for item in items:
                media_id = ''
                videoName = item['videoName']
                if verify_name:
                    if videoName == keyword:
                        media_id = item['id']
                else:
                    media_id = item['id']
                if media_id:
                    rst = self._session.get(url=f'{self._endpoint}/video/detail?videoId={media_id}')
                    try:
                        video_info = rst.json()['data']
                        categoryId = video_info['categoryId']
                        subjectId = video_info['subjectId']
                        durationSec = video_info['durationSec']
                        if durationSec:
                            videos_info.append([media_id, categoryId, subjectId, durationSec])
                        else:
                            print(f'该视频的时长为空:{media_id}')
                    except:
                        print(f"获取单个视频异常:{media_id}")
        if videos_info:
            return videos_info
        else:
            raise Exception('获取到的直播信息为空')

    # 向ck插入数据
    def _insert_ck(self, media, categoryId, subjectId, duration, mediaType, your_duration):
        if your_duration > duration and duration != -1:
            your_duration = duration
        et = tools.get_time_stamp()
        st = tools.get_time_stamp(seconds=-your_duration)
        rid = f"5c77bd3519a26c624d{str(randint(100000, 999999))}_00"
        data = {"requests": [
          {
            "uid": self._user_id,
            "platform": "android",
            "appId": 201,
            "channel": 214,
            "categoryId": categoryId,
            "subjectId": subjectId,
            "mediaType": mediaType,
            "mediaId": media,
            "mediaItemId": -1,
            "rid": rid,
            "sp": 0,
            "ep": your_duration,
            "st": st,
            "et": et,
            "sr": 1,
            "tt": duration,
            "ip": "192.168.40.83",
            "version": "4.3.9",
            "device": "HUAWEI HUAWEI NXT-AL10",
            "kernel": "7.0",
            "watchDuration": your_duration,
            "resolved1": "",
            "extra": {}
          }
        ]
        }
        logger.debug(data)
        params = urlencode(data)
        url = f'{self._ck_endpoint}:38000/h/com.haixue.watchlog.api.service.WatchLogService/saveOrUpdate'
        logger.debug(url)
        rst = requests.post(url=url, params=params)
        try:
            msg = f'向ck插入数据成功:{rst.json()}'
            logger.info(msg)
        except:
            errmsg = '向ck插入数据失败'
            logger.warning(errmsg)

    # 提交评价
    def _contentappraise(self, media, contentType):
        data = {'req':
            {
                "contentType": contentType,
                "contentId": media,
                "type": 1,
                "appId": 204,
                "customerId": self._user_id,
                "score": 5,
                "comment": "15378487",
                "labelIds": [
                    0
                ]
            }
                  }
        logger.debug(data)
        params = urlencode(data)
        url = f'{self._ck_endpoint}:32200/h/com.haixue.appraise.api.ContentAppraiseDetailApi/add'
        logger.debug(url)
        rst = requests.post(url=url, params=params)
        try:
            msg = f'提交评价成功{rst.json()}'
            logger.info(msg)
        except:
            errmsg = '提交评价失败'
            logger.warning(errmsg)


    # 插入直播，第一次上报
    _insert_ck_type0 = partial(_insert_ck, duration=-1, mediaType=0)

    # 插入录播，第一次上报
    _insert_ck_type2 = partial(_insert_ck, mediaType=2)

    # 评价直播
    _contentappraise_live = partial(_contentappraise, contentType=1)

    # 评价录播
    _contentappraise_video = partial(_contentappraise, contentType=2)

    def insert_ck_lives(self, keyword=None, verify_name=False, page=1, your_duration=30, add_contentappraise=False):
        lives_info = self._get_live_info_type0(keyword=keyword, verify_name=verify_name, page=page)
        for live in lives_info:
            media = live[0]
            categoryId = live[1]
            subjectId = live[2]
            self._insert_ck_type0(self, media=media, categoryId=categoryId, subjectId=subjectId,
                                  your_duration=your_duration)
            if add_contentappraise:
                self._contentappraise_live(self, media)

    def insert_ck_video(self, keyword=None, verify_name=False, page=1, your_duration=30, add_contentappraise=False):
        video_info = self._get_video_info_type2(keyword=keyword, verify_name=verify_name, page=page)
        for video in video_info:
            media = video[0]
            categoryId = video[1]
            subjectId = video[2]
            duration = video[3]
            # 当设置的时长大于视频时长时，取视频时长
            self._insert_ck_type2(self, media=media, categoryId=categoryId, subjectId=subjectId, duration=duration,
                                  your_duration=your_duration)
            if add_contentappraise:
                self._contentappraise_video(self, media)

    # 插入直播并提交对直播的评价
    insert_ck_lives_add_appraise = partial(insert_ck_lives, add_contentappraise=True)

    # 通过直播名称精确搜索，插入直播
    insert_ck_lives_verifyname = partial(insert_ck_lives, verify_name=True)

    # 通过直播名称精确搜索，插入直播并提交对直播的评价
    insert_ck_lives_add_appraise_verifyname = partial(insert_ck_lives, verify_name=True, add_contentappraise=True)


    # 插入录播并提交对录播的评价
    insert_ck_video_add_appraise = partial(insert_ck_video, add_contentappraise=True)

    # 通过录播名称精确搜索，插入录播
    insert_ck_video_verifyname = partial(insert_ck_video, verify_name=True)

    # 通过录播名称精确搜索，插入录播并提交对录播的评价
    insert_ck_video_add_appraise_verifyname = partial(insert_ck_video, verify_name=True, add_contentappraise=True)


if __name__ == "__main__":

    # 插入100条数据到ck，一个用户观看多个直播
    op = InsertCK(23880547)
    # op.insert_ck_lives_add_appraise_verifyname(op, keyword='拉取回2')
    # op.insert_ck_lives_add_contentappraise(op, page=2)
    # op.insert_ck_video_add_appraise_verifyname(op, keyword='第3篇 （6）室内消火栓系统', your_duration=1800)
    op.insert_ck_video_verifyname(op, keyword='第4篇 （1）石油化工防火', your_duration=1800)

