#!/usr/bin/env python
# -*- coding:utf-8 -*-

import bs4  # TODO: import for what?
from bs4 import BeautifulSoup
import requests
from http import cookiejar
import re
import os

import config


def get_html_text(url):
    try:
        kv = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'}
        r = requests.get(url, timeout=30, headers=kv)
        r.raise_for_status()  # 检查状态码
        r.encoding = r.apparent_encoding
        return r.text
    except:  # too broad exception clause
        return "产生异常"


def get_formhash(url):
    formhash_text = get_html_text(url)
    formhash_soup = BeautifulSoup(formhash_text, 'lxml')
    formhash_tag = formhash_soup.find('input', attrs={'name': 'formhash'})
    formhash = formhash_tag('value')
    return formhash


class Guest:

    def __init__(self):
        self.username = config.USERNAME
        self.password = config.PASSWORD
        self.formhash = get_formhash(config.FORMHASHURL)
        self.cookie = cookiejar.CookieJar()
        self.pattern = re.compile(r'tid=\d{6}')  # 摄影天地
        # self.pattern = re.compile(r'normalthread_\d{6}')  # 缘聚睿思

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;",
            "Accept-Encoding": "gzip",
            "Accept-Language": "zh-CN,zh;q=0.8",
            'Connection': 'keep-alive',
            "Referer": config.REFERER,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
        }

    def login(self):

        payload = {
            'username': self.username,
            'password': self.password,
            'quickforward': 'yes',
            'handlekey': 'ls'
        }

        wb_data = requests.post(config.LOGINURL, data=payload, headers=self.headers, cookies=self.cookie)
        wb_data.raise_for_status()
        wb_data.encoding = wb_data.apparent_encoding
        cookies = wb_data.cookies
        global cookies
        if '欢迎您回来' in wb_data.text:
            self.formhash = get_formhash(config.REFERER)
            print('登陆成功')
        else:
            print('登陆失败')

    def get_post_url(self, fid):
        forumurl = config.FORUMURL + str(fid)+'&page=2'
        wb_data = requests.get(forumurl)
        wb_data.raise_for_status()
        wb_data.encoding = wb_data.apparent_encoding
        # soup = BeautifulSoup(wb_data.text,'lxml')
        id_ = self.pattern.findall(str(wb_data.text))
        id_set = set(id_)
        id_list = list(id_set)
        post_url = []
        for i in id_list:
            # post_url.append(config.DOMAIN+'forum.php?mod=viewthread&tid='+i[-6:]+'&extra=page%3D1')
            post_url.append(config.DOMAIN+'forum.php?mod=viewthread&tid='+i[-6:]+'&extra=page=2')
        print(post_url)
        return post_url

    def download(self, url):
        root = 'D:\\pics\\561\\'  # 摄影天地
        path = root+url.split("/")[-1]
        try:
            if not os.path.exists(root):
                os.mkdir(root)
            if not os.path.exists(path):
                r = requests.get(url, headers=self.headers, cookies=cookies)
                with open(path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                    print(path+'  succeed')
        except:  # too broad exception clause
            print(path)
            print("失败一次")   # 有url包含非法字符 ?

    def get_picture(self, url):
        for i in url:
            wb_data = requests.get(i, headers=self.headers, cookies=cookies)
            soup = BeautifulSoup(wb_data.text, 'lxml')
            # td = soup.find('td',attrs={'class': 't_f'}) # 缘聚睿思
            div = soup.find('div', attrs={'class': 't_fsz'})  # 摄影天地
            if div is None:
                print("div is none")
            else:
                img = div.find_all('img', attrs={'class': 'zoom'})
                for j in img:
                    if j['file'][0] == 's':
                        pass
                    elif j['file'][0] == 'h':
                        self.download(j['file'])
                    elif j['file'][0] == '.':
                        self.download(config.DOMAIN + i[2:])
                    else:
                        pass


me = Guest()
me.login()
# me.get_picture(me.get_post_url(217))  # 缘聚睿思
me.get_picture(me.get_post_url(561))  # 摄影天地
