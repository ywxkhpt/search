# -*- coding:utf-8 -*-

from LinkedInSpider import LinkedinSpider, Account
from configure import *


def run(name):
    """
    运行主函数
    :param name: 搜索的人名
    :return: 用户信息
    """
    # 待搜索内容
    KEYWORDS = name

    # 获取账号
    twitter_account = Account()
    l_account = twitter_account.get_account()
    # 登陆账号采集
    spider = LinkedinSpider(name=KEYWORDS)
    # spider.main(linkedin_account=l_account[0],
    #             linkedin_password=l_account[1])
    return spider.main(linkedin_account=account,
                linkedin_password=password)


if __name__ == '__main__':
    run("billor")
