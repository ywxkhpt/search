# -*- coding:utf-8 -*-
# facebook爬虫

from FacebookSpider import *


def run(name):
    # 推文数据库
    tweetHost = 'localhost'
    tweetDatabase = 'twitter_test'
    tweetCollection = 'twitter_filter'
    # 待搜索内容
    # KEYWORDS = 'uestc OR like OR black OR funny OR lucy since:2018-10-01 until:2018-10-03'
    # 获取账号
    # twitter_account = Account()
    # t_account = twitter_account.get_account()
    # 登陆账号采集
    spider = FacebookSpider(name)
    result = spider.main()
    print result


if __name__ == "__main__":
    run('mikeng')
