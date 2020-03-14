# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 17:28
# @Author  : Key-lei
# @File    : 02-urldecode.py
from urllib import parse
import time


def url_encode(url):
    first_decode = parse.quote(url)
    second_decode = parse.quote(first_decode)
    return second_decode


def url_decode(url):
    first_encode = parse.unquote(url)
    second_encode = parse.unquote(first_encode)
    return second_encode


print(int(time.time()))
# '1584111275'
ts = time.localtime(1583503736)
now = time.strftime("%Y-%m-%d %H:%M:%S", ts)
now1 = time.localtime(1583503736)
print(now)
