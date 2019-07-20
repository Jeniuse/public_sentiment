# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy import FormRequest
import requests
from lxml import etree
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json

# 国家广播电视总局
class hhtcsSpider(scrapy.Spider):
    name = 'logint'
    allowed_domains = ['bbs.lcdhome.net']
    keyword = '户户通'
    start_urls = [
        "http://bbs.lcdhome.net"
    ]
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    }
    send_headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        "Host":"bbs.lcdhome.net",
        "Refer":"http://bbs.lcdhome.net/"
    }
    page_num = 1 # 页码

    def start_requests(self):
        return [Request("http://bbs.lcdhome.net/login.php",meta={'cookiejar':1},callback=self.login,method="POST")]

    def parse(self, response):
        print(type(response.body))
        print(response.body)
        print(response.body.decode('gbk'))

    def login(self, response):
        time.sleep(6)
        data = {
            "pwuser": "hhtzhiboxing",
            "pwpwd": "1qaz2wsx",
            "question":"0",
            "step":"2",
            "lgt":"0",
            "customquest":"",
            "answer":"",
            "head_login":"",
            "jumpurl":"http://bbs.lcdhome.net/index.php"
        }
        return [FormRequest.from_response(response,
                                          meta={'cookiejar':response.meta['cookiejar']},
                                          headers=self.send_headers,
                                          formdata=data,
                                          callback=self.after_login)]
    def after_login(self, response):
        return [Request("http://bbs.lcdhome.net/searcher.php?keyword=%s&type=thread&threadrange=1&username=&starttime=&endtime=&fid=&sortby=postdate&page=1"%self.keyword,
                meta={'cookiejar':response.meta['cookiejar']},
                headers=self.headers,callback=self.parse)]