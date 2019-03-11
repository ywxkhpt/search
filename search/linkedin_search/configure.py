# -*- coding:utf-8 -*-
from urllib import quote_plus
from search.util.config_read_util import *

# 代理
PROXY = 'kb111.asuscomm.com:8118'
# 推特账户
account = 'hptuestc@gmail.com'
password = "he19910824"
# 要搜索的内容
# KEYWORDS = '@spam since:2018-10-01 until:2018-11-01'

# 领英用户数据库
# userHost = 'mongodb://kb314:fzdwxxcl.314@121.49.99.14:30011'
# userHost = "mongodb://%s:%s@%s" % (quote_plus('readAnyDatabase'), quote_plus('Fzdwxxcl.121'), '121.49.99.14:30011')
# userDatabase = 'Account'
# userCollection = 'twitter'

USER = config_read("database.ini", "mongodb", "USER")
PASSWORD = config_read("database.ini", "mongodb", "PASSWORD")
HOST = config_read("database.ini", "mongodb", "HOST")
# userHost = "mongodb://%s:%s@%s" % (USER, PASSWORD, HOST)
userHost = "mongodb://%s" % (HOST)
userDatabase = config_read("database.ini", "collection_facebook", "database")
userCollection = config_read("database.ini", "collection_facebook", "collection")
