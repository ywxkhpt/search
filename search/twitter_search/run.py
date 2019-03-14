# -*- coding:utf-8 -*-
# 功能：在推特搜索栏输入相应的内容“A”，抓取和“A”想关的用户信息
from API import API, Account
from configure import *


def run(name):
    """
    爬取搜索主函数
    :param name: 搜索的人名
    :return: 爬取的结果
    """
    # 待搜索内容
    KEYWORDS = name

    # 获取账号
    twitter_account = Account()
    t_account = twitter_account.get_account()
    # 登陆账号采集
    Crawler = API(proxy=PROXY, keywords=KEYWORDS)
    return Crawler.crawler(twitter_account=t_account[0],
                           twitter_password=t_account[1])


if __name__ == "__main__":
    run('bill')
