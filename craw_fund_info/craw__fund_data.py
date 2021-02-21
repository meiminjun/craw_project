# encoding:utf-8
# FileName: craw_project
# Author:   wzg
# email:    1010490079@qq.com
# Date:     2021/1/27 15:50
# Description: 爬取天天基金网收益的Top基金
import json
import random
import re
import time
from collections import OrderedDict
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append("..")
from craw_tools.get_ua import get_ua

# 显示所有列

pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)


def resolve_rank_info(data):
    """
    解析每一页的所有基金的收益数据
    @param data:
    @return:
    """
    rank_pages_data = []
    data = data.replace("[", "").replace("]", "").replace("\"", "")
    for data_row in data.split(","):
        # 生成一个有序字典，保存排序结果
        rank_info = OrderedDict()
        row_arr = data_row.split("|")

        if len(row_arr) > 16:
            # 获取每个星级的评分
            rank_info['基金代码'] = 'd'+row_arr[0]
            rank_info['基金名称'] = row_arr[1]
            rank_info['截止日期'] = row_arr[3]
            rank_info['单位净值'] = row_arr[4]
            rank_info['日增长率'] = row_arr[5]
            rank_info['近1周'] = row_arr[6]
            rank_info['近1月'] = row_arr[7]
            rank_info['近3月'] = row_arr[8]
            rank_info['近6月'] = row_arr[9]
            rank_info['近1年'] = row_arr[10]
            rank_info['近2年'] = row_arr[11]
            rank_info['近3年'] = row_arr[12]
            rank_info['今年来'] = row_arr[13]
            rank_info['成立来'] = row_arr[14]
            rank_info['起购金额'] = row_arr[-5]
            rank_info['原手续费'] = row_arr[-4]
            rank_info['现手续费'] = row_arr[-3]

            # 保存当前rank信息
            rank_pages_data.append(rank_info)

    return rank_pages_data


def get_rank_data(url, page_index, max_page, fund_type):
    """
    根据起始页码获取当前页面的所有基金情况
    :return:
    """
    try_cnt = 0
    rank_data = []
    # 若当前页其实页码小于总页数 或者 超时3次 则退出
    while page_index < max_page and try_cnt < 3:
        # 根据每页数据条数确定起始下标
        new_url = url + '?ft=' + fund_type + '&sc=1n&st=desc&pi=' + \
            str(page_index) + '&pn=100&fl=0&isab=1'
        print(f"正在爬取第 {page_index} 页数据：{new_url}")
        # print('正在爬取第 {0} 页数据：{1}'.format(page_index, new_url))
        # 爬取当前页码的数据
        response = requests.get(url=new_url, headers={
                                'User-Agent': get_ua()}, timeout=10)
        if len(response.text) > 100:
            # 匹配数据并解析
            res_data = re.findall("\[{1}\S+\]{1}", response.text)[0]
            # 解析单页数据
            rank_pages_data = resolve_rank_info(res_data)
            rank_data.extend(
                rank_page_data for rank_page_data in rank_pages_data)
        else:
            try_cnt += 1
        page_index += 1

        # 随机休眠3-5 秒
        time.sleep(random.randint(3, 5))

    df_rank_data = pd.DataFrame(rank_data)
    return df_rank_data


def resolve_rank_detail_info(fund_code, response):
    """
    解析基金的详细数据
    @param fund_code:
    @param response:
    @return:
    """
    rank_detail_info = OrderedDict()

    soup = BeautifulSoup(response.text, 'html.parser')
    rank_detail_info['基金代码'] = 'd'+fund_code
    soup_div = soup.find_all('div', class_='bs_gl')[0]
    rank_detail_info['成立日期'] = soup_div.find_all(
        'label')[0].find_all('span')[0].get_text()
    rank_detail_info['基金经理'] = soup_div.find_all(
        'label')[1].find_all('a')[0].get_text()
    rank_detail_info['类型'] = soup_div.find_all(
        'label')[2].find_all('span')[0].get_text()
    rank_detail_info['管理人'] = soup_div.find_all(
        'label')[3].find_all('a')[0].get_text()
    rank_detail_info['资产规模'] = soup_div.find_all('label')[4].find_all(
        'span')[0].get_text().replace("\r\n", "").replace(" ", "")

    return rank_detail_info


def resolve_position_info(fund_code, text):
    """
    解析基金的持仓数据
    @param fund_code:
    @param text:
    @return:
    """
    fund_positions_data = []
    res_data = re.findall(r'\"(.*)\"', text)[0]
    soup = BeautifulSoup(res_data, 'html.parser')

    soup_tbody = soup.find_all('table', class_='w782 comm tzxq')[
        0].find_all('tbody')[0]
    for soup_tr in soup_tbody.find_all('tr'):
        postion_info = OrderedDict()
        postion_info['基金代码'] = 'd'+fund_code
        postion_info['基金截止日期'] = soup.find_all(
            'font', class_='px12')[0].get_text()

        postion_info['持仓排序'] = soup_tr.find_all('td')[0].get_text()
        postion_info['持仓股票代码'] = 'd' + \
            soup_tr.find_all('td')[1].find_all('a')[0].get_text()
        postion_info['持仓股票名称'] = soup_tr.find_all(
            'td')[2].find_all('a')[0].get_text()
        postion_info['持仓股票最新价'] = soup_tr.find_all(
            'td')[3].find_all('span')[0].get_text()
        postion_info['持仓股票涨跌幅'] = soup_tr.find_all(
            'td')[4].find_all('span')[0].get_text()
        postion_info['持仓股票占比'] = soup_tr.find_all('td')[6].get_text()
        postion_info['持仓股票持股数'] = soup_tr.find_all('td')[7].get_text()
        postion_info['持仓股票持股市值'] = soup_tr.find_all(
            'td')[8].get_text().replace(",", "")

        fund_positions_data.append(postion_info)

    return fund_positions_data


def try_craw_info(fund_code, try_cnt):
    """
    @param fund_code:
    @return:
    """
    if try_cnt > 5:
        return None, None
    try:
        '''爬取页面，获得该基金的详细数据'''
        position_title_url = "http://fundf10.eastmoney.com/ccmx_" + \
            str(fund_code[1:]) + ".html"
        print('第 {0} 次尝试，正在爬取基金 {1} 的详细数据中...'.format(try_cnt, fund_code[1:]))
        response_title = requests.get(url=position_title_url, headers={
                                      'User-Agent': get_ua()}, timeout=10)

        """爬取页面，获取该基金的持仓数据"""
        position_data_url = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=" + \
                            str(fund_code[1:]) + "&topline=10&year=&month=&rt=" + \
            str(random.uniform(0, 1))
        print('第 {0} 次尝试，正在爬取基金 {1} 的持仓情况中...'.format(try_cnt, fund_code[1:]))
        # 解析基金的持仓情况
        response_data = requests.get(url=position_data_url, headers={
                                     'User-Agent': get_ua()}, timeout=10)

        # 解析基金的详细数据
        rank_detail_info = resolve_rank_detail_info(
            fund_code[1:], response_title)
        fund_positions_data = resolve_position_info(
            fund_code[1:], response_data.text)
        time.sleep(random.randint(2, 4))
    except:
        time.sleep(random.randint(2*try_cnt, 4*try_cnt))
        print("{0} 基金数据爬取失败，请注意！".format(str(fund_code[1:])))
        rank_detail_info, fund_positions_data = try_craw_info(
            fund_code, try_cnt+1)

    return rank_detail_info, fund_positions_data


def get_position_data(data, rank):
    """
    根据起始页码获取当前页面的所有Top数据
    @param data:
    @param rank:
    @return:
    """
    """筛选Top数据"""
    data = data.replace('', np.NaN, regex=True)
    data_notna = data.dropna(subset=['近1年'])
    data_notna['近1年'] = data_notna['近1年'].astype(float)
    data_sort = data_notna.sort_values(by='近1年', ascending=False)
    data_rank = data_sort.loc[0:rank-1, :]

    # 爬取每个基金的数据
    rank_detail_data = []
    position_data = []
    error_funds_list = []
    for row_index, data_row in data_rank.iterrows():
        fund_code = str(data_row['基金代码'])
        try:
            '''爬取页面，获得该基金的详细数据'''
            position_title_url = "http://fundf10.eastmoney.com/ccmx_" + \
                str(fund_code[1:]) + ".html"
            print('正在爬取第 {0}/{1} 个基金 {2} 的详细数据中...'.format(row_index +
                                                           1, len(data_rank), fund_code[1:]))
            response_title = requests.get(url=position_title_url, headers={
                                          'User-Agent': get_ua()}, timeout=10)
            # 解析基金的详细数据
            rank_detail_info = resolve_rank_detail_info(
                fund_code[1:], response_title)

            """爬取页面，获取该基金的持仓数据"""
            position_data_url = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code=" + \
                                str(fund_code[1:]) + "&topline=10&year=&month=&rt=" + \
                str(random.uniform(0, 1))
            print('正在爬取第 {0}/{1} 个基金 {2} 的持仓情况中...'.format(row_index +
                                                           1, len(data_rank), fund_code[1:]))
            # 解析基金的持仓情况
            response_data = requests.get(url=position_data_url, headers={
                                         'User-Agent': get_ua()}, timeout=10)
            fund_positions_data = resolve_position_info(
                fund_code[1:], response_data.text)

            # 保存数据
            rank_detail_data.append(rank_detail_info)
            position_data.extend(
                fund_position_data for fund_position_data in fund_positions_data)
        except:
            error_funds_list.append(fund_code)
            print("{0} 数据爬取失败，稍后会进行重试，请注意！".format(str(fund_code[1:])))
        # 随机休眠2-4 秒
        time.sleep(random.randint(2, 4))

    """爬取失败的进行重试"""
    for fund_info in error_funds_list:
        rank_detail_data_try, position_data_try = try_craw_info(fund_info, 1)
        if rank_detail_data_try == '':
            # 保存数据
            rank_detail_data.append(rank_detail_data_try)
            position_data.extend(
                fund_position_data for fund_position_data in position_data_try)

    df_rank_detail_data = pd.DataFrame(rank_detail_data)
    df_position_data = pd.DataFrame(position_data)

    return df_rank_detail_data, df_position_data


if __name__ == '__main__':
    # 获取每个类型中的基金
    url = 'https://fundapi.eastmoney.com/fundtradenew.aspx'
    page_index = 1
    max_page = 100
    # 分别对应偏股基金：pg、股票基金：gp、混合基金：hh、债券基金：zq、指数基金：zs
    fund_type = 'zs'
    # 得到详细的月、年收益情况
    df_rank_data = get_rank_data(url, page_index, max_page, fund_type)
    # 得到Top的基金权重
    max_rank = 300 if int(len(df_rank_data)/100) > 3 else 100
    # 获取基金详细信息和持仓情况
    df_rank_detail_data, df_position_data = get_position_data(
        df_rank_data, max_rank)
    # 合并收益数据和详情数据
    df_rank_data = df_rank_data.merge(
        df_rank_detail_data, on='基金代码', how="outer",)
    df_rank_data = df_rank_data.fillna('--')
    """保存数据"""
    df_rank_data.to_csv(r'file/' + fund_type +
                        '_型基金收益详情.csv', encoding='gbk', index=False)
    df_position_data.to_csv(r'file/' + fund_type + '_型基金近一年Top' +
                            str(max_rank) + '前十大持仓.csv', encoding='gbk', index=False)
