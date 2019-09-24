# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
import ast
import json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcngd'
    allowed_domains = ['gbdsj.gd.gov.cn/']
    start_urls = [
        "http://search.gd.gov.cn/api/search/all?keywords=%s&page=1"%"直播卫星",
        "http://search.gd.gov.cn/api/search/all?keywords=%s&page=1"%"中星九号",
        "http://search.gd.gov.cn/api/search/all?keywords=%s&page=1"%"扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def start_requests(self):
        yield scrapy.FormRequest(
            url='http://search.gd.gov.cn/api/search/all',
            formdata={
                'keywords': '直播卫星',
                'page': '1',  # 这里不能给int类型的1，requests模块中可以
                'time_from': '1537703217',
                'time_to':'1569239217'
            },
        callback = self.parse
        )
        yield scrapy.FormRequest(
            url='http://search.gd.gov.cn/api/search/all',
            formdata={
                'keywords': '扶贫工程',
                'page': '1',
                'time_from': '1537703853',
                'time_to': '1569239853'
            },
            callback=self.parse
        )
        yield scrapy.FormRequest(
            url='http://search.gd.gov.cn/api/search/all',
            formdata={
                'keywords': '中星九号',
                'page': '1',
            },
            callback=self.parse
        )

    def parse(self, response):
        html = str(response.text)
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        html = html.split('list":[{', 1)[1]
        html = html.split('}],"total"', 1)[0]
        html = str(html).encode('unicode_escape').decode("unicode_escape")
        docs = html.split("},{")
        for doc in docs:
            try:
                doc = '{' + doc + '}'
                doc_dict = ast.literal_eval(doc)
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = str(doc_dict['title'])
                item["title"] = item["title"].replace('<em>','')
                item["title"] = item["title"].replace('</em>', '')
                item["title"] = item["title"].replace('<\\\\/em>', '')
                item["title"] = item["title"].replace('[', '')
                item["title"] = item["title"].replace(']', '')
                item["url"] = str(doc_dict['url']).replace('\\','')
                item["urlId"] = item["url"].split('post_')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, id)
                item["time"] = doc_dict['pub_time']
                info = str(doc_dict['content'])
                if TimeMarch.time_March(item["time"], self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//div[@calss='article-content']/p/text() | //div[@calss='article-content']//p/text() | //div[@id='content']//span/text()")
                item["info"] = "".join(item["info"])
                if len(item["info"]) < len(info):
                    item["info"] = info
                yield item
            except:
                print()
        self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫