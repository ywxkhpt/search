# -*- coding:utf-8 -*-
import sys

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
    # 类变量
    path = os.path.join(path_dir_parent(__file__) + "/data/logging/LinkedIn_search.log")
    value = "('" + path + "', 'a')"
    config_set("logging.ini", "handler_hand02", "args", value)
    log_util()
    logger_name = "LinkedIn_search"
    logger = logging.getLogger(logger_name)

    def __init__(self, name):

        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument('--proxy-server=%s' % PROXY)  # 用代理跑driver
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.keywords = name
        self.information_list = []

    def login(self):
        # 访问linkedin网页
        self.browser.get('https://www.linkedin.com/')
        # 输入账户密码
        self.browser.find_element_by_name('session_key').clear()
        self.browser.find_element_by_name('session_key').send_keys(account)
        time.sleep(2)
        self.browser.find_element_by_name('session_password').clear()
        self.browser.find_element_by_name('session_password').send_keys(password)
        time.sleep(2)
        # 模拟点击登录按钮，两种不同的点击方法。。。
        try:
            self.browser.find_element_by_id('login-submit').send_keys(Keys.ENTER)
            time.sleep(3)
        except:
            error = account, "login error!"
            self.logger.info(error)
            return False

        success = account, "login success!"
        self.logger.info(success)
        return True

    def search(self):
        try:
            for i in range(1, 100):
                i = str(i)
                url = "https://www.linkedin.com/search/results/all/?keywords=" + self.keywords + "&page=" + i
                time.sleep(3)
                self.browser.get(url)
                self.find_user()
        except Exception, e:
            error = "error:", e.message
            self.logger.info(error)
        self.logger.info("crawler success")
        return self.information_list

    def find_user(self):
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
        # ActionChains(self.driver).send_keys(Keys.DOWN).perform()
        ActionChains(self.browser).send_keys(Keys.END).perform()  # 拉到底
        wait = randint(3, 5)
        time.sleep(wait)

    def main(self):
        login = self.login()
        if login:
            search = self.search()
            return search


if __name__ == '__main__':
    spider = LinkedinSpider("tom")
    spider.main()
