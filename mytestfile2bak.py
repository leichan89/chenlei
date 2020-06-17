import datetime
import time
from urllib.parse import urlencode
import requests
from random import randint
from functools import partial


valid_media = []

user_id = 15378501


headers = {'Cookie': 'SESSION=NzRhOTA5ZGItNjg2My00YWRkLTgyNjEtODQzNzI0ZGIzMzI0'}

env = 'reg'

if env == 'test0':
    endpoint = 'https://api-study-web.test0.highso.com.cn'
    ck_endpoint = 'http://192.168.16.250'
elif env == 'reg':
    endpoint = 'https://api-study-web.reg.highso.com.cn'
    ck_endpoint = 'http://123.126.133.247'
elif env == 'stage':
    endpoint = 'https://api-study-web.stage.highso.com.cn'
    ck_endpoint = 'http://123.126.133.237'

def get_time_stamp(days=0, hours=0, minutes=0, seconds=0):
    '''
    生成指定日期时间戳，可以是之前的或者之后的日期，默认生成当前日期
    :param days: 天数
    :param hours: 小时
    :param minutes: 分钟
    :param seconds: 秒
    :return:
    '''
    try:
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        n_days = now + delta
        timeArray = time.strptime(n_days.strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
        # 转为时间戳
        timeStamp = int(time.mktime(timeArray)) * 1000
        return timeStamp
    except:
        errmsg = '生成时间错异常, days, hours, minutes, seconds必须是整数'
        print(errmsg)

# 获取直播的信息，类别、科目、id信息
def get_live_info_type0(keyword=None, by_name=False, page=1):
    live_info = []
    if keyword:
        params = {"page": 1, "size": page * 100, "keyword": keyword}
    else:
        params = {"page": 1, "size": page * 100}
    rst = requests.get(url=f'{endpoint}/live/page', params=params, headers=headers)
    try:
        items = rst.json()['data']['items']
    except:
        raise Exception('获取直播信息失败')
    if items:
        for item in items:
            livename = item['liveName']
            if by_name:
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
        raise Exception('获取到的直播信息为空')

# 获取直播的信息，类别、科目、id信息
def get_video_info_type2(keyword=None, by_name=False, page=1):
    videos_info = []
    if keyword:
        params = {"page": 1, "size": page * 100, "keyword": keyword}
    else:
        params = {"page": 1, "size": page * 100}
    try:
        rst = requests.get(url=f'{endpoint}/video/page', params=params, headers=headers)
        items = rst.json()['data']['items']
    except:
        raise Exception('获取直播列表信息异常')
    if items:
        for item in items:
            media_id = ''
            videoName = item['videoName']
            if by_name:
                if videoName == keyword:
                    media_id = item['id']
            else:
                media_id = item['id']
            if media_id:
                rst = requests.get(url=f'{endpoint}/video/detail?videoId={media_id}', headers=headers)
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
def insert_ck(media, categoryId, subjectId, duration, mediaType):

    et = get_time_stamp()
    st = get_time_stamp(seconds=-30)
    randstr = str(randint(100000, 999999))
    data = {"requests": [
      {
        "uid": user_id,
        "platform": "android",
        "appId": 201,
        "channel": 214,
        "categoryId": categoryId,
        "subjectId": subjectId,
        "mediaType": mediaType,
        "mediaId": media,
        "mediaItemId": -1,
        "rid": f"5c77bd3519a26c624d{randstr}_00",
        "sp": 0,
        "ep": 30,
        "st": st,
        "et": et,
        "sr": 1,
        "tt": duration,
        "ip": "192.168.40.83",
        "version": "4.3.9",
        "device": "HUAWEI HUAWEI NXT-AL10",
        "kernel": "7.0",
        "watchDuration": 30,
        "resolved1": "",
        "extra": {}
      }
    ]
    }

    params = urlencode(data)
    rst = requests.post(url=f'{ck_endpoint}:38000/h/com.haixue.watchlog.api.service.WatchLogService/saveOrUpdate', params=params)
    try:
        print(f'向ck插入数据成功:{rst.json()}')
    except:
        print("向ck插入数据失败")

# 提交评价
def contentappraise(media, contentType):
    p_data = {'req':
        {
            "contentType": contentType,
            "contentId": media,
            "type": 1,
            "appId": 204,
            "customerId": user_id,
            "score": 5,
            "comment": "15378487",
            "labelIds": [
                0
            ]
        }
              }

    params = urlencode(p_data)
    rst = requests.post(url=f'{ck_endpoint}:32200/h/com.haixue.appraise.api.ContentAppraiseDetailApi/add', params=params)
    try:
        print(f'提交评价成功{rst.json()}')
    except:
        print('提交评价失败')



# 插入直播，第一次上报
insert_ck_type0 = partial(insert_ck, duration=-1, mediaType=0)

# 插入录播，第一次上报
insert_ck_type2 = partial(insert_ck, mediaType=2)

# 评价直播
contentappraise_live = partial(contentappraise, contentType=1)

# 评价录播
contentappraise_video = partial(contentappraise, contentType=2)

if __name__ == "__main__":

    # 插入1000条数据到ck，一个用户观看多个直播
    # rst = get_live_info_type0(page=10)
    # medias = []
    # for r in rst:
    #     media = r[0]
    #     categoryId = r[1]
    #     subjectId = r[2]
    #     medias.append(media)
    #     insert_ck_type0(media, categoryId, subjectId)
    #     contentappraise_live(media)
    # print(medias)
    rst = get_video_info_type2(page=100)
    print(rst)


