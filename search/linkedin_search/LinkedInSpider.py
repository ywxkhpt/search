# -*- coding:utf-8 -*-
import sys

from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

reload(sys)
sys.setdefaultencoding('utf-8')

import logging
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver import ActionChains
from random import randint
from configure import *
from search.util.config_read_util import config_set
from search.util.logger_util import log_util
from search.util.path_util import path_dir_parent


class LinkedinSpider(object):
    """
    设置日志文件路径
    """
    # 类变量
    path = os.path.join(path_dir_parent(__file__) + "/data/logging/LinkedIn_search.log")
    value = "('" + path + "', 'a')"
    config_set("logging.ini", "handler_hand02", "args", value)
    log_util()
    logger_name = "LinkedIn_search"
    logger = logging.getLogger(logger_name)

    def __init__(self, name):
        """
        初始化浏览器选项
        :param name:
        """
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--proxy-server=%s' % PROXY)  # 用代理跑driver
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.keywords = name
        self.information_list = []

    def login(self, linkedin_account, linkedin_password):
        """
        登陆函数
        :return: 登陆结果
        """
        # 访问linkedin网页
        self.browser.get('https://www.linkedin.com/')
        WebDriverWait(self.browser, 60).until(expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "login-form")))
        # 输入账户密码
        self.browser.find_element_by_name('session_key').clear()
        self.browser.find_element_by_name('session_key').send_keys(linkedin_account)
        time.sleep(2)
        self.browser.find_element_by_name('session_password').clear()
        self.browser.find_element_by_name('session_password').send_keys(linkedin_password)
        time.sleep(2)
        # 模拟点击登录按钮，两种不同的点击方法。。。
        try:
            self.browser.find_element_by_id('login-submit').send_keys(Keys.ENTER)
            time.sleep(3)
        except:
            error = linkedin_account, "login error!"
            print error
            # self.logger.info(error)
            return False

        success = linkedin_account, "login success!"
        print success
        # self.logger.info(success)
        return True

    def search(self):
        """
        跳转到搜索界面
        :return: 用户名 个人主页 用户信息
        """
        try:
            for i in range(1, 50):
                i = str(i)
                url = "https://www.linkedin.com/search/results/all/?keywords=" + self.keywords + "&page=" + i
                time.sleep(3)
                self.browser.get(url)
                self.find_user()
        except Exception, e:
            error = "error:", e.message
            # self.logger.info(error)
            print error
        # self.logger.info("crawler success")
        print "crawler success"
        return self.information_list

    def find_user(self):
        """
        解析函数 找出用户名 个人主页
        :return: 个人信息
        """
        information = {}
        lis = self.browser.find_elements_by_class_name("search-result__occluded-item")
        self.page_down()
        for li in lis:
            tag = li.find_element_by_tag_name("a")
            href = tag.get_attribute("href")
            information["person_url"] = href
            span = li.find_element_by_css_selector(".name.actor-name")  # class之间的空格 表示是复合类 可以用这种方式查找
            name = span.text
            information["user_name"] = name
            self.logger.info(information)
            self.information_list.append(information)

    def page_down(self):
        """
        下拉函数
        :return:
        """
        # ActionChains(self.driver).send_keys(Keys.DOWN).perform()
        ActionChains(self.browser).send_keys(Keys.END).perform()  # 拉到底
        wait = randint(3, 5)
        time.sleep(wait)

    def main(self,linkedin_account,linkedin_password):
        """
        主运行函数
        :return: 搜索结果
        """
        login = self.login(linkedin_account,linkedin_password)
        if login:
            search = self.search()
            return search


# 链接领英用户信息数据库
class linkedinClient(object):
    def __init__(self, linkedin_host, linkedin_database, linkedin_collection):
        self.client = MongoClient(linkedin_host)
        self.database = self.client.get_database(linkedin_database)
        self.collection = self.database.get_collection(linkedin_collection)
        self.create_unique_index()

    def create_unique_index(self):
        self.collection.ensure_index([("id", 1)], unique=True)

    def update_data(self, key_str, key, data):  # 根据唯一标示key，更新数据库的内容
        self.collection.update({key_str: key}, {'$set': data}, upsert=True)


# 链接领英账户数据库
class Account(object):
    def __init__(self):
        self.client = MongoClient(userHost)
        self.database = self.client.get_database(userDatabase)
        self.collection = self.database.get_collection(userCollection)

    def get_account(self):
        """
        获取领英账户用户名 密码
        :return: 用户名 密码
        """
        account = self.collection.find({}).skip(randint(0, 600)).limit(1)[0]
        return account['account'], account['password']


if __name__ == '__main__':
    pass
