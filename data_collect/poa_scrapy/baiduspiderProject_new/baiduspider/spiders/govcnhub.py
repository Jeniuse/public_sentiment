# -*- coding: utf-8 -*-
import scrapy
import time
import json
import ast
import requests
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 湖北省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnhub'
    allowed_domains = ['gdj.hubei.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://gdj.nx.gov.cn')

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限

    def parse(self, response):
        with open('./keywords.txt', 'r', encoding='utf8') as fp:
            keywords = json.loads(fp.read())
        start_urls = []
        for keyword in keywords:
            start_urls.append(
                'http://gdj.hubei.gov.cn/igs/front/search.jhtml?code=03074fc5eaae4cd5b5be57bd3fe4e9b6&orderBy=time&pageNumber=2&pageSize=10&searchWord=%s&siteId=22&timeOrder=desc'%keyword)
        for url in start_urls:
            timecount = 0  # 计数器
            flag = True
            page_num = 0
            while flag:
                response = requests.get(url)
                item = BaiduspiderItem()
                item = inititem(item)
                # 是否符合爬取条件
                item['IsFilter'] = False
                html = str(response.text)
                html = html.split('content":[{', 1)[-1].split('}],')[0]
                docs = html.split('},{')
                for doc in docs:
                    try:
                        doc = '{' + doc + '}'
                        doc_dict = ast.literal_eval(doc)
                        item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        item['source'] = ['网站', '500010000000004']
                        item["title"] = str(doc_dict['title'])
                        item["url"] = str(doc_dict['url'])
                        item["urlId"] = item["url"].split('_')[-1].split('.')[0]
                        item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                        item["time"] = doc_dict['trs_time'].split('T')[0]
                        info = str(doc_dict['content'])
                        if TimeMarch.time_March(item["time"], self.default_scope_day):
                            item["IsFilter"] = True
                        else:
                            item["IsFilter"] = False
                            timecount = timecount + 1
                        res_child = child_page(item["url"])
                        item["info"] = res_child.xpath("//div[@calss='TRS_UEDITOR TRS_WEB']//p/text() | //div[@calss='article-content']//p/text() | //div[@id='content']//span/text()")
                        item["info"] = "".join(item["info"])
                        if len(item["info"]) < len(info):
                            item["info"] = info
                        yield item
                    except:
                        print()
                if timecount < self.allowed_timesup and page_num<5:
                    keyword = url.split('searchWord=')[1].split('&')[0]
                    page_num = url.split('pageNumber=')[1].split('&')[0]
                    print('\n第***********************************%s***********************************页\n' % page_num)
                    page_num = int(page_num) + 1
                    NextPageUrl = 'http://gdj.hubei.gov.cn/igs/front/search.jhtml?code=03074fc5eaae4cd5b5be57bd3fe4e9b6&orderBy=time&pageNumber=%s&pageSize=10&searchWord=%s&siteId=22&timeOrder=desc'% (str(page_num),keyword)
                    print(NextPageUrl)
                    url = NextPageUrl
                else:
                    flag = False
        self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫
