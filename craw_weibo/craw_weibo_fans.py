# encoding:utf-8
# FileName: craw_weibo_fans
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/11/11 18:54
# Description:
import random
import re
import time
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import numpy as np
import warnings

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


def get_ua():
    """
    在UA库中随机选择一个UA
    :return: 返回一个库中的随机UA
    """
    ua_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
        "Opera/8.0 (Windows NT 5.1; U; en)",
        "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Macintosh; U; IntelMac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    return random.choice(ua_list)


def get_page_info(url, index):
    """
    获取单页内容并解析
    @param url:
    @param index:
    @return:
    """
    header = {'User-Agent': get_ua()}
    '''爬取页面，获得详细数据'''
    response = requests.get(url=url, headers=header, timeout=10)

    fans_list = []
    try:
        if 'cards' in response.json()['data']:
            card_group = response.json()['data']['cards'][0]['card_group']
        else:
            card_group = response.json()['data']['cardlistInfo']['cards'][0]['card_group']

        """解析粉丝列表"""
        print("爬取第{0}页粉丝列表，当前页获取到{1}个粉丝".format(index + 1, len(card_group)))
        for card_info in card_group:
            # 用户名
            screen_name = card_info['user']['screen_name']
            # 用户id
            id = card_info['user']['id']
            # 主页链接
            profile_url = card_info['user']['profile_url']
            # 关注人数
            follow_count = card_info['user']['follow_count']
            # 粉丝数
            followers_count = card_info['user']['followers_count']
            # 总动态数
            statuses_count = card_info['user']['statuses_count']
            # 签名
            description = card_info['user']['description']
            # 是否认证：否/false
            verified = card_info['user']['verified']
            # 性别：男/m
            gender = card_info['user']['gender']
            # 用户uid
            # uid = url[url.rfind('u/')+2 : url.rfind('?')]

            fans_list.append([screen_name, id, profile_url, follow_count, followers_count,
                              statuses_count, description, verified, gender])
    except Exception as e:
        print(e)

    fans_column = ['用户名', '用户id', '主页链接', '关注人数', '粉丝数', '总动态数', '签名', '是否认证', '性别']
    fans_data = pd.DataFrame(fans_list, columns=fans_column)

    return fans_data


def get_master_info(uids):
    """
    获取关注数和粉丝数
    @param uids:
    @return:
    """
    master = {}
    url = "https://m.weibo.cn/profile/info?uid=" + uids
    response = requests.get(url=url, headers={'User-Agent': get_ua()}, timeout=10)

    master['screen_name'] = response.json()['data']['user']['screen_name']
    # 关注人数
    master['follow_count'] = response.json()['data']['user']['follow_count']
    # 粉丝数
    master['followers_count'] = response.json()['data']['user']['followers_count']
    # 总动态数
    master['statuses_count'] = response.json()['data']['user']['statuses_count']
    # 签名
    master['description'] = response.json()['data']['user']['description']
    # 是否认证：否/false
    master['verified'] = response.json()['data']['user']['verified']
    # 性别：男/m
    master['gender'] = response.json()['data']['user']['gender']

    return master


def standardize_date(created_at):
    '''
    标准化微博发布时间"
    :param created_at:
    :return:
    '''
    # CST时间转换为标准时间
    if '+0800' in created_at:
        created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(created_at, '%a %b %d %H:%M:%S +0800 %Y'))

        return created_at

    if u"刚刚" in created_at:
        created_at = datetime.now().strftime("%Y-%m-%d")
    elif u"分钟" in created_at:
        minute = created_at[:created_at.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
    elif u"小时" in created_at:
        hour = created_at[:created_at.find(u"小时")]
        hour = timedelta(hours=int(hour))
        created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
    elif u"昨天" in created_at:
        day = timedelta(days=1)
        created_at = (datetime.now() - day).strftime("%Y-%m-%d")
    elif created_at.count('-') == 1:
        year = datetime.now().strftime("%Y")
        created_at = year + "-" + created_at

    return created_at


def filter_emoij(text):
    """
    过滤emoij表情符
    @param text:
    @return:
    """
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    text = co.sub('', text)

    return text


def get_fans_info(url):
    """
    获取粉丝详细数据
    @param urls:
    @return:
    """
    response = requests.get(url=url, headers={'User-Agent': get_ua()}, timeout=10)
    print(url)
    fans = {}
    try:
        if 'user' in response.json()['data']:
            fans['statuses_count'] = response.json()['data']['user']['statuses_count']
            fans['description'] = filter_emoij(response.json()['data']['user']['description'])
            fans['gender'] = response.json()['data']['user']['gender']
        else:
            fans['statuses_count'] = None
            fans['description'] = None
            fans['gender'] = None

        # 曾经有发过微博，则取最近的一条
        if 'statuses' in response.json()['data'] and len(response.json()['data']['statuses'])>0:
            fans['created_at'] = datetime.strptime(standardize_date(response.json()['data']['statuses'][0]['created_at']),
                                                   "%Y-%m-%d %H:%M:%S")
            fans['text'] = filter_emoij(response.json()['data']['statuses'][0]['text'])
            fans['source'] = filter_emoij(response.json()['data']['statuses'][0]['source'])
        else:
            fans['created_at'], fans['text'], fans['source'] = '', '', ''
    except Exception as e:
        print(e)

    return fans


if __name__ == '__main__':
    uid = 'xxxxxxx'
    """获取详情数据"""
    master_info = get_master_info(uids=uid)
    print("用户id:{0}，发博数:{1}，关注{2}人，拥有粉丝{3}人".format(
        uid, master_info['statuses_count'], master_info['follow_count'], master_info['followers_count']))

    """设置最大页数"""
    fans_count = master_info['followers_count']
    # 由于当page大于250时就已经无法得到内容了，所以要设置最大页数为250
    max_page = fans_count//20 + 1 if fans_count < 5000 else 250

    # 爬取数据
    fans_data = pd.DataFrame()
    for i in range(max_page):
        index = i*20
        url_fans = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{0}&since_id={1}".format(uid, index)
        data_per_page = get_page_info(url_fans, i)
        fans_data = fans_data.append(data_per_page)
        sleep(3)
    fans_data.to_csv('weibo_{0}_fans_1.csv'.format(uid), encoding='gbk', index=False)

    """爬取每个粉丝的详情数据"""
    for fans in fans_data.iterrows():
        fans_url = "https://m.weibo.cn/profile/info?uid=" + str(fans[1]['用户id'])
        fan_info = get_fans_info(fans_url)

        # 获取并更新每个粉丝最近的一条微博动态
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '总动态数'] = fan_info['statuses_count']
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '最近一次发博日期'] = fan_info['created_at']
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '最近一次发博内容'] = fan_info['text']
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '最近一次发博终端'] = fan_info['source']
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '签名'] = fan_info['description']
        fans_data.loc[fans_data['用户id'] == fans[1]['用户id'], '性别'] = fan_info['gender']
        sleep(3)

    # 保存数据
    fans_data.to_csv('weibo_{0}_fans.csv'.format(uid), encoding='utf-8', index=False)