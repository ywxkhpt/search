# -*- coding:utf-8 -*-
# 功能：在推特搜索栏输入相应的内容“A”，抓取和“A”想关的推文中的目标内容
# KEYWORDS = '@spam since:2013-01-01 until:2015-02-20'
from API import API, Account
from configure import *


def run(name):
    # 推文数据库
    tweetHost = 'localhost'
    tweetDatabase = 'twitter_test'
    tweetCollection = 'twitter_filter'
    # 待搜索内容
    # KEYWORDS = 'uestc OR like OR black OR funny OR lucy since:2018-10-01 until:2018-10-03'
    KEYWORDS = name

    # 获取账号
    # twitter_account = Account()
    # t_account = twitter_account.get_account()
    # 登陆账号采集
    Crawler = API(proxy=PROXY, keywords=KEYWORDS)
    Crawler.crawler(twitter_account=account,
                    twitter_password=password,
                    host=tweetHost, database=tweetDatabase, collection=tweetCollection)


if __name__ == "__main__":
    run('bill')
