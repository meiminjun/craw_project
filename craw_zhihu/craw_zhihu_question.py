# encoding:utf-8
# FileName: craw_zhihu_question
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/11/23 14:11
# Description: 获取知乎某个问题下所有回答
import json
import re
import time
from datetime import datetime
from time import sleep

import pandas as pd
import numpy as np
import warnings

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from craw_tools.get_ua import get_ua

warnings.filterwarnings('ignore')

# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)


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


def get_question_base_info(url):
    """
    获取问题的详细描述
    @param url:
    @return:
    """
    response = requests.get(url=url, headers={'User-Agent': get_ua()}, timeout=10)
    # print(response.text.replace('\u200b', '').replace('\u2022', ''))

    """获取数据并解析"""
    soup = BeautifulSoup(response.text, 'lxml')
    # 问题标题
    title = soup.find("h1", {"class": "QuestionHeader-title"}).text
    # 具体问题
    question = ''
    try:
        question = soup.find("div", {"class": "QuestionRichText--collapsed"}).text.replace('\u200b', '')
    except Exception as e:
        print(e)
    # 关注者
    follower = int(soup.find_all("strong", {"class": "NumberBoard-itemValue"})[0].text.strip().replace(",", ""))
    # 被浏览
    watched = int(soup.find_all("strong", {"class": "NumberBoard-itemValue"})[1].text.strip().replace(",", ""))
    # 问题回答次数
    answer_str = soup.find_all("h4", {"class": "List-headerText"})[0].span.text.strip()
    # 抽取xxx 个回答中的数字：【正则】数字出现次数>=0
    answer_count = int(re.findall('\d*', answer_str)[0])

    # 问题标签
    tag_list = []
    tags = soup.find_all("div", {"class": "QuestionTopic"})
    for tag in tags:
        tag_list.append(tag.text)

    return title, question, follower, watched, answer_count, tag_list


def init_url(question_id, limit, offset):
    """
    构造每一页访问的url
    @param question_id:
    @param limit:
    @param offset:
    @return:
    """
    base_url_start = "https://www.zhihu.com/api/v4/questions/"
    base_url_end = "/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed" \
                   "%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by" \
                   "%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count" \
                   "%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info" \
                   "%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting" \
                   "%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B" \
                   "%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics" \
                   "&limit={0}&offset={1}".format(limit, offset)

    return base_url_start + question_id + base_url_end


def get_time_str(timestamp):
    """
    将时间戳转换为标准日期字符
    @param timestamp:
    @return:
    """
    datetime_str = ''
    try:
        # 时间戳timestamp 转datetime时间格式
        datetime_time = datetime.fromtimestamp(timestamp)
        # datetime时间格式转为日期字符串
        datetime_str = datetime_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(e)
        print("日期转换错误")

    return datetime_str


def get_answer_info(url, index):
    """
    解析问题回答
    @param url:
    @param index:
    @return:
    """
    response = requests.get(url=url, headers={'User-Agent': get_ua()}, timeout=10)
    text = response.text.replace('\u200b', '')

    per_answer_list = []
    try:
        question_json = json.loads(text)
        """获取当前页的回答数据"""
        print("爬取第{0}页回答列表，当前页获取到{1}个回答".format(index + 1, len(question_json["data"])))
        for data in question_json["data"]:
            """问题的相关信息"""
            # 问题的问题类型、id、提问类型、创建时间、修改时间
            question_type = data["question"]['type']
            question_id = data["question"]['id']
            question_question_type = data["question"]['question_type']
            question_created = get_time_str(data["question"]['created'])
            question_updated_time = get_time_str(data["question"]['updated_time'])

            """答主的相关信息"""
            # 答主的用户名、签名、性别、粉丝数
            author_name = data["author"]['name']
            author_headline = data["author"]['headline']
            author_gender = data["author"]['gender']
            author_follower_count = data["author"]['follower_count']

            """回答的相关信息"""
            # 问题回答id、创建时间、更新时间、赞同数、评论数、具体内容
            id = data['id']
            created_time = get_time_str(data["created_time"])
            updated_time = get_time_str(data["updated_time"])
            voteup_count = data["voteup_count"]
            comment_count = data["comment_count"]
            content = data["content"]

            per_answer_list.append([question_type, question_id, question_question_type, question_created,
                                    question_updated_time, author_name, author_headline, author_gender,
                                    author_follower_count, id, created_time, updated_time, voteup_count, comment_count,
                                    content
                                    ])

    except:
        print("Json格式校验错误")
    finally:
        answer_column = ['问题类型', '问题id', '问题提问类型', '问题创建时间', '问题更新时间',
                         '答主用户名', '答主签名', '答主性别', '答主粉丝数',
                         '答案id', '答案创建时间', '答案更新时间', '答案赞同数', '答案评论数', '答案具体内容']
        per_answer_data = pd.DataFrame(per_answer_list, columns=answer_column)

    return per_answer_data


if __name__ == '__main__':
    # question_id = '424516487'
    question_id = '429548386'
    url = "https://www.zhihu.com/question/" + question_id
    """获取问题的详细描述"""
    title, question, follower, watched, answer_count, tag_list = get_question_base_info(url)
    print("问题url："+ url)
    print("问题标题：" + title)
    print("问题描述：" + question)
    print("该问题被定义的标签为：" + '、'.join(tag_list))
    print("该问题关注人数：{0}，已经被 {1} 人浏览过".format(follower, watched))
    print("截止 {}，该问题有 {} 个回答".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), answer_count))

    """获取问题的回答数据"""
    # 构造url
    limit, offset = 20, 0
    page_cnt = int(answer_count/limit) + 1
    answer_data = pd.DataFrame()
    for page_index in range(page_cnt):
        answer_url = init_url(question_id, limit, offset+page_index*limit)
        # 获取数据
        data_per_page = get_answer_info(answer_url, page_index)
        answer_data = answer_data.append(data_per_page)
        sleep(3)

    answer_data.to_csv('凡尔赛沙雕语录_{0}.csv'.format(question_id), encoding='utf-8', index=False)