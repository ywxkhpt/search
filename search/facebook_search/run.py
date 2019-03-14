# -*- coding:utf-8 -*-
# facebook爬虫

from FacebookSpider import *
from configure import *


def run(name):
    # 待搜索内容
    KEYWORDS = name

    # 获取账号
    facebook_account = Account()
    f_account = facebook_account.get_account()
    # 登陆账号采集
    spider = FacebookSpider(proxy=PROXY, keywords=KEYWORDS)
    return spider.main(account=f_account[0],
                       password=f_account[1])
    # return spider.main(account=account,
    #                    password=password)


if __name__ == "__main__":
    run('mikeng')
