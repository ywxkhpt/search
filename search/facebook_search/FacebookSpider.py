# -*- coding:utf-8 -*-

import sys
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
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.expected_conditions import alert_is_present

from configure import *
from search.util.config_read_util import config_set
from search.util.logger_util import log_util
from search.util.path_util import path_dir_parent


class FacebookSpider(object):
    # 类变量
    path = os.path.join(path_dir_parent(__file__) + "/data/logging/facebook_search.log")
    value = "('" + path + "', 'a')"
    config_set("logging.ini", "handler_hand03", "args", value)
    log_util()
    logger_name = "facebook_search"
    logger = logging.getLogger(logger_name)

    def __init__(self, keywords):

        self.chrome_options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values':
                {
                    'notifications': 2
                }
        }
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.chrome_options.add_argument('--proxy-server=%s' % PROXY)  # 用代理跑driver
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options)
        self.keywords = keywords

    def login(self, email, password):

        # browser.implicitly_wait(10)
        # browser.set_window_size(0,0)
        # 访问facebook网页
        self.browser.get('https://www.facebook.com/login.php?login_attempt=1&lwv=110/')
        # 输入账户密码
        self.browser.find_element_by_id('email').clear()
        self.browser.find_element_by_id('email').send_keys(email)
        time.sleep(2)
        self.browser.find_element_by_id('pass').clear()
        self.browser.find_element_by_id('pass').send_keys(password)
        time.sleep(2)
        # 模拟点击登录按钮，两种不同的点击方法。。。
        try:
            self.browser.find_element_by_xpath('//button[@id="loginbutton"]').send_keys(Keys.ENTER)
            time.sleep(3)
            # self.browser.find_element_by_xpath('//input[@tabindex="4"]').send_keys(Keys.ENTER)
            # self.browser.find_element_by_xpath('//a[@href="https://www.facebook.com/?ref=logo"]').send_keys(Keys.ENTER)
        except:
            error = email, "login error!"
            self.logger.info(error)
            return False

        success = email, "login success!"
        self.logger.info(success)
        return True

    def search(self):
        url = "https://www.facebook.com/search/people/?q=" + self.keywords + "&epa=SERP_TAB"
        self.browser.get(url)
        try:
            WebDriverWait(self.browser, 60).until(expected_conditions.presence_of_element_located
                                                  ((By.ID, 'initial_browse_result')))
            # Alert(self.browser).accept()
            flag = True
        except NoSuchElementException:
            flag = False
            self.logger.info("search fail")
        return flag

    def page_down(self):
        # ActionChains(self.browser).send_keys(Keys.DOWN).perform()
        ActionChains(self.browser).send_keys(Keys.END).perform()  # 拉到底
        wait = randint(3, 6)
        time.sleep(wait)

    def find_user(self):
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

                # 将数据插入到数据库中
                # _client.update_data(key_str='id', key=tweet_id, data=tweet_dic)
                print "**********************************\n"
        except Exception as Err:
            error = "error:", Err.message
            # print error
            self.logger.info(error)
        self.logger.info("crawler success")
        return information_list

    def main(self):
        login = self.login(account, password)
        if login:
            search = self.search()
            if search:
                self.browser.close()
                return self.find_user()


if __name__ == '__main__':
    spider = FacebookSpider("mike")
    result = spider.main()
    print result
