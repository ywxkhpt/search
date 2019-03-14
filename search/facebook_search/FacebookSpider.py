# -*- coding:utf-8 -*-

import sys

from pymongo import MongoClient

reload(sys)
sys.setdefaultencoding('utf-8')

import logging
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import ActionChains
from random import randint
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from configure import *
from search.util.config_read_util import config_set
from search.util.logger_util import log_util
from search.util.path_util import path_dir_parent
from selenium.webdriver.support import expected_conditions


class FacebookSpider(object):
    """
    设置日志文件
    """
    # 类变量
    path = os.path.join(path_dir_parent(__file__) + "/data/logging/facebook_search.log")
    value = "('" + path + "', 'a')"
    config_set("logging.ini", "handler_hand03", "args", value)
    log_util()
    logger_name = "facebook_search"
    logger = logging.getLogger(logger_name)

    def __init__(self, proxy, keywords):
        """
        初始化浏览器选项
        :param proxy: 代理
        :param keywords: 搜索关键词
        """
        self.chrome_options = webdriver.ChromeOptions()
        # 不弹出通知
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }
        # self.chrome_options.add_argument('--headless')
        # self.chrome_options.add_argument('--disable-gpu')
        # self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.chrome_options.add_argument('--proxy-server=%s' % proxy)  # 用代理跑driver
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.keywords = keywords

    def login(self, email, password):
        """
        登陆函数
        :param email: 邮箱
        :param password: 密码
        :return: 登陆结果
        """
        # 访问facebook网页
        self.browser.get('https://www.facebook.com/')
        WebDriverWait(self.browser, 60).until(expected_conditions.presence_of_element_located(
            (By.ID, "login_form")))
        # 输入账户密码
        self.browser.find_element_by_id('email').clear()
        self.browser.find_element_by_id('email').send_keys(email)
        time.sleep(2)
        self.browser.find_element_by_id('pass').clear()
        self.browser.find_element_by_id('pass').send_keys(password)
        time.sleep(2)
        # 模拟点击登录按钮，两种不同的点击方法。。。
        try:
            self.browser.find_element_by_id('loginbutton').send_keys(Keys.ENTER)
            time.sleep(3)
        except Exception, e:
            print e.message
            error = email, "login error!"
            print error
            # self.logger.info(error)
            return False

        success = email, "login success!"
        print success
        # self.logger.info(success)
        return True

    def search(self):
        """
        跳转到搜索界面
        :return: 搜索是否成功
        """
        url = "https://www.facebook.com/search/people/?q=" + self.keywords + "&epa=SERP_TAB"
        self.browser.get(url)
        try:
            WebDriverWait(self.browser, 60).until(expected_conditions.presence_of_element_located
                                                  ((By.ID, 'initial_browse_result')))
            flag = True
        except NoSuchElementException:
            flag = False
            print "search fail"
            # self.logger.info("search fail")
        return flag

    def page_down(self):
        """
        下拉函数
        :return:
        """
        ActionChains(self.browser).send_keys(Keys.END).perform()  # 拉到底
        wait = randint(3, 6)
        time.sleep(wait)

    def find_user(self):
        """
        解析函数
        :return: 用户名 主页链接信息
        """
        information_list = []  # 返回信息
        try:
            count = 0
            while True:
                tags = self.browser.find_elements_by_class_name('_32mo')  # 获取当前显示的用户（逐条）
                if count == len(tags):
                    break
                count = len(tags)
                self.page_down()
            print time.ctime(), "开始采集新的用户......."
            tags = self.browser.find_elements_by_class_name('_32mo')  # 获取当前显示的用户（逐条）
            count = len(tags)
            print time.ctime(), 'len_tags:', count
            # 获取每一条的详细信息
            for num in range(0, count):
                div = tags[num]
                user_dic = {}
                try:
                    # 用户的个人主页
                    person_url = div.get_attribute("href")
                    # 用户的user_name
                    user_name = div.text
                except NoSuchElementException:
                    continue

                # 用户信息
                user_dic['person_url'] = person_url
                user_dic['user_name'] = user_name
                information_list.append(user_dic)

                information = 'person_url:', person_url, 'user_name:', user_name
                self.logger.info(information)
        except Exception as Err:
            error = "error:", Err.message
            print error
            # self.logger.info(error)
        # self.logger.info("crawler success")
        print "crawler success"
        return information_list

    def main(self, account, password):
        """
        运行主函数
        :param account: 账户名
        :param password: 密码
        :return: 爬取的搜索结果
        """
        login = self.login(account, password)
        if login:
            search = self.search()
            if search:
                return self.find_user()


# 链接facebook用户信息数据库
class facebookClient(object):
    def __init__(self, facebook_host, facebook_database, facebook_collection):
        self.client = MongoClient(facebook_host)
        self.database = self.client.get_database(facebook_database)
        self.collection = self.database.get_collection(facebook_collection)
        self.create_unique_index()

    def create_unique_index(self):
        self.collection.ensure_index([("id", 1)], unique=True)

    def update_data(self, key_str, key, data):  # 根据唯一标示key，更新数据库的内容
        self.collection.update({key_str: key}, {'$set': data}, upsert=True)


# 链接facebook账户数据库
class Account(object):
    def __init__(self):
        self.client = MongoClient(userHost)
        self.database = self.client.get_database(userDatabase)
        self.collection = self.database.get_collection(userCollection)

    def get_account(self):
        """
        获取facebook账户用户名 密码
        :return: 用户名 密码
        """
        account = self.collection.find({}).skip(randint(0, 70)).limit(1)[0]
        return account['account'], account['pwd']


if __name__ == '__main__':
    pass
