# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 17:16
# @Author  : Key-lei
# @File    : 01-全名小视频.py
import os
import requests
import re
from app爬虫 import urldecode
import json
import time

# 先拿到主页 然后通过主页进行data主合
# 然后批量进行下载
# 加密方式为两次encode加密

# post 表单分析
# 其中ext能够在第一页找到然后一依次提取ext构造新表单
"""
# 第一页
workspage=ext={"authorId":"gj88_xHwtiDmA93jj9LVuQ","authorType":"ugc"}&refresh_state=0
# 往后的每一页
workspage=ext={"authorId":"gj88_xHwtiDmA93jj9LVuQ","authorType":"ugc"}&refresh_state=2&pgext={"refresh_time":1584092030,"list_min_time":15840658444439}

"""
# url 为图片中提到的连接
url = 'https://quanmin.hao222.com/feedvideoui/api?pd=author_share_mvideo&ucenter=ext%3D%257B%2522metiaId%2522%253A%2522uP9XlEaWRdRb5I74iuYozQ%2522%252C%2522authorType%2522%253A%2522ugc%2522%252C%2522authorId%2522%253A%2522uP9XlEaWRdRb5I74iuYozQ%2522%257D'


class AppSpider:

    def __init__(self, url):
        self.url = url
        self.target_url = 'https://quanmin.baidu.com/mvideo/api?log=vhk&tn=1021212c&ctn=1021212c&imei=865166023548475&cuid=D786A042E9D75A80529EDFAD318BC2FE|0&bdboxcuid=null&os=android&osbranch=a0&ua=1080_1920_480&ut=SM-G9730_5.1.1_22_samsung&uh=samsung,android_x86,SM-G9730,1&apiv=1.0.0.10&appv=123&version=1.15.5.10&life=1584070542&clife=1584070542&hid=2E712ABC3F55F16F0298C2B3C66B64E8&network=1&sids=2595_3&api_name=workspage&sign=b5a5f61a0c7a44dcb5ca6a27be42d679'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; YAL-AL00 Build/LMY49I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 bdminivideo/1.15.5.10 arsdk/240 (Baidu; P1 5.1.1)",
            "Referer": "https://quanmin.baidu.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            'Host': 'quanmin.baidu.com'
        }

    def get_ugc_author_id(self):
        ugc_author_id = urldecode.url_decode(self.url)
        result = re.findall('"authorType":"(.*?)","authorId":"(.*?)"', ugc_author_id)
        a, b = result[0]
        return a, b

    def get_author_name(self, u, author_id):
        """

        :param u: ugc
        :param author_id:  author_id
        :return: 作者的名字
        """

        data = 'mine=ext={"authorId":"%s","authorType":"%s"}' % (author_id, u)
        response = requests.post(self.url, data=data, verify=False, headers=self.headers)
        data_text = response.text
        author_name = re.findall("window.userMeta =.*?username: '(.*?)'.*?};", data_text, re.S)
        return author_name[0]

    def get_1_page(self, u, author_id):
        data = 'workspage=ext={"authorId":"%s","authgorType":"%s"}&refresh_state=0' % (author_id, u)
        response = requests.post(self.target_url, data=data, headers=self.headers, verify=False)
        json_data = response.json()
        worklist = json_data['workspage']['data']['worksList']
        ext = json_data['workspage']['data']['ext']
        ext_dict = json.loads(ext)
        list_min_time = ext_dict['list_min_time']
        for work in worklist:
            ts = time.localtime(int(list_min_time / 10000))
            lis_min_time_data = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            print(f"第1页,最后上传时间{lis_min_time_data}")
            mp4_url = work['playurl']
            title = str(mp4_url).split('/')[-1].split('.')[-2]
            print(mp4_url, title)
            self.download_mp4(mp4_url, title)
        return ext

    def get_next_all_pages(self, u, author_id, ext, i):
        """

        :param u:
        :param author_id:
        :param ext:  分析出 页面的改变是通过etc修改
        :param i: 打印的页数
        :return:
        """
        # 构造data
        data = 'workspage=ext={"authorId":"%s","authgorType":"%s"}&refresh_state=2&refresh_state=2&pgext=' % (
            author_id, u)
        data_next = data + ext
        response = requests.post(self.target_url, data=data_next, headers=self.headers, verify=False,
                                 allow_redirects=False)
        json_data = response.json()
        # 获取ext 目标上传视频文件的最后时间 通过抓包分析到这个参数是会变得
        ext1 = json_data['workspage']['data']['ext']
        ext1_dict = json.loads(ext1)
        list_min_time = ext1_dict['list_min_time']
        print('#' * 50)
        worklist = json_data['workspage']['data']['worksList']
        for work in worklist:
            ts = time.localtime(int(list_min_time / 10000))
            lis_min_time_data = time.strftime("%Y-%m-%d %H:%M:%S", ts)
            print(f"正在爬取第{i}页,最后上传时间{lis_min_time_data}")
            mp4_url = work['playurl']
            title = str(mp4_url).split('/')[-1].split('.')[-2]
            print(mp4_url, title)
            self.download_mp4(mp4_url, title)
        return ext1

    def download_mp4(self, url, title):
        """

        :param url:
        :param title:
        :return:
        """
        ugc, author = self.get_ugc_author_id()
        # 作者名字用于创建文件
        auther_name = self.get_author_name(ugc, author)
        path = os.getcwd() + u'/%s/' % auther_name
        if not os.path.isdir(path):
            os.mkdir(path)
        response_mp4 = requests.get(url)
        filename = path + title + '.mp4'
        print(f'{title}正在下载')
        with open(filename, mode='wb') as fp:
            fp.write(response_mp4.content)
        print(f'{title}下载完毕,文件位于{path}')


if __name__ == '__main__':
    app = AppSpider(url)
    ugc, author = app.get_ugc_author_id()
    ext1 = app.get_1_page(ugc, author)
    ext2 = app.get_next_all_pages(ugc, author, ext1, 2)
    # app.get_author_name(ugc, author)
    # 默认爬取10页可以自行修改
    # 可以将range修改 可以实现爬取全部的视频
    for i in range(100):
        if ext2:
            ext2 = app.get_next_all_pages(ugc, author, ext2, i + 2)
        else:
            print('已经爬取完毕')
        print('下载完毕')
