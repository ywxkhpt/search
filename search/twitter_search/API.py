# -*- coding:utf-8 -*-
# 功能：twitter用户搜索
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium import webdriver
import time
from configure import *
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from random import randint
from search.util.config_read_util import config_read, config_set
from search.util.path_util import path_dir_parent
from pymongo import MongoClient
from search.util.logger_util import log_util
import logging
import os


class API(object):
    # 类变量
    path = os.path.join(path_dir_parent(__file__) + "/data/logging/twitter_search.log")
    value = "('" + path + "', 'a')"
    config_set("logging.ini", "handler_hand01", "args", value)
    log_util()
    logger_name = "twitter_search"
    logger = logging.getLogger(logger_name)

    # 对象变量
    def __init__(self, proxy, keywords):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--proxy-server=%s' % proxy)  # 用代理跑driver
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        self.keywords = keywords

    def login(self, email, pass_word):
        """
        登录函数
        :param email:
        :param pass_word:
        :return:
        """
        login_url = 'https://twitter.com/login/'
        while True:
            self.driver.get(login_url)
            try:
                WebDriverWait(self.driver, 180).until(expect.presence_of_element_located(
                    (By.CLASS_NAME, "js-username-field")))
                print "tying to login now......"
                self.driver.find_element_by_class_name('js-username-field').send_keys(email)
                time.sleep(3)
                self.driver.find_element_by_class_name('js-password-field').send_keys(pass_word)
                time.sleep(3)
                self.driver.find_element_by_css_selector('button.submit').click()
                WebDriverWait(self.driver, 60).until(expect.presence_of_element_located
                                                     ((By.CLASS_NAME, "topbar-tweet-btn")))
                print email, "login success!"
                return True
            except NoSuchElementException:
                print email, "login fail!(Can't find expect elements)"
                self.driver.refresh()
                time.sleep(3)
                continue
            except TimeoutException:
                print email, "login fail for time out!"
                time.sleep(3)
                continue

    def search(self):

        self.driver.get("https://twitter.com/search?f=users&vertical=news&q=" + self.keywords + "&src=typd")
        # self.driver.find_element_by_class_name('search-input').send_keys(self.keywords)
        # self.driver.find_element_by_class_name('search-icon').click()
        try:
            WebDriverWait(self.driver, 60).until(expect.presence_of_element_located
                                                 ((By.CLASS_NAME, 'SearchNavigation-titleText')))
            flag = True
        except NoSuchElementException:
            flag = False
        return flag

    def parse(self, the_tweet_host, the_tweet_database, the_tweet_collection):
        information_list = [] #返回信息
        try:
            count = 0
            while True:
                tags = self.driver.find_elements_by_class_name('ProfileCard-userFields')  # 获取当前显示的用户（逐条）
                if count == len(tags):
                    break
                count = len(tags)
                self.page_down()
            print time.ctime(), "开始采集新的网页......."
            tags = self.driver.find_elements_by_class_name('ProfileCard-userFields')  # 获取当前显示的用户（逐条）
            # tags = self.driver.find_elements_by_class_name('js-stream-item')  # 获取当前显示的用户（逐条）
            count = len(tags)
            print time.ctime(), 'len_tags:', count
            # 获取每一条的详细信息
            for num in range(0, count):
                div = tags[num]
                user_dic = {}
                # print time.ctime()  # , '\n', 'div:', div
                #  采集推文相关信息
                try:
                    person_details = div.find_element_by_css_selector(
                        ".ProfileCard-screennameLink.u-linkComplex.js-nav")
                except NoSuchElementException:
                    continue
                # 用户的个人主页
                person_url = person_details.get_attribute('href')
                # 用户的user_name
                screen_name = person_details.text
                # 用户的screen_name
                span = div.find_element_by_css_selector(
                    ".fullname.ProfileNameTruncated-link.u-textInheritColor.js-nav")
                user_name = span.text

                # 用户信息
                user_dic['person_url'] = person_url
                user_dic['user_name'] = user_name
                user_dic['screen_name'] = screen_name
                information_list.append(user_dic)

                information = 'person_url:', person_url, 'screen_name:', screen_name, 'user_name:', user_name
                self.logger.info(information)
                # print 'person_url:', person_url, 'screen_name:', screen_name, 'user_name:', user_name

                # 将数据插入到数据库中
                # _client.update_data(key_str='id', key=tweet_id, data=tweet_dic)
                print "**********************************\n"
        except Exception as Err:
            print Err.message, "error......"
        return information_list

    def page_down(self):
        for i in range(3):
            # ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.END).perform()  # 拉到底
            wait = randint(3, 10)
            time.sleep(wait)

    def crawler(self, twitter_account, twitter_password, host, database, collection):
        # user_account = Account()
        # _account = user_account.collection.find({'alive': {"$exists": False}}).skip(6).limit(1)[0]
        # account = _account['account']
        # password = _account['pwd']
        page = self.login(twitter_account, twitter_password)  # 尝试登录，登录成功则继续执行
        if page:
            self.search()
            self.parse(the_tweet_host=host, the_tweet_database=database, the_tweet_collection=collection)
            self.logger.info("crawler success")
            print "crawler success"
        else:
            self.logger.info("login error")
            print "login error"
        self.driver.quit()


# 链接推文数据库
class TweetsClient(object):
    def __init__(self, tweet_host, tweet_database, tweet_collection):
        self.client = MongoClient(tweet_host)
        self.database = self.client.get_database(tweet_database)
        self.collection = self.database.get_collection(tweet_collection)
        self.create_unique_index()

    def create_unique_index(self):
        self.collection.ensure_index([("id", 1)], unique=True)

    def update_data(self, key_str, key, data):  # 根据唯一标示key，更新数据库的内容
        self.collection.update({key_str: key}, {'$set': data}, upsert=True)


# 链接推特账户数据库
class Account(object):
    def __init__(self):
        self.client = MongoClient(userHost)
        self.database = self.client.get_database(userDatabase)
        self.collection = self.database.get_collection(userCollection)

    def get_account(self):
        account = self.collection.find({}).skip(randint(0, 100)).limit(1)[0]
        return account['account'], account['pwd']
