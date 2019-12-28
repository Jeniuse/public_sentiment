# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
import ast
import json
# 广东省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcngd'
    allowed_domains = ['gbdsj.gd.gov.cn/']

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限

    def start_requests(self):
        # 广东只能获取post数据，通过formrequest方式访问，取回的数据处理成字典自动获取
        with open('./keywords.txt', 'r', encoding='utf8') as fp:
            keywords = json.loads(fp.read())
        for keyword in keywords:
            yield scrapy.FormRequest(
                url='http://search.gd.gov.cn/api/search/all',
                formdata={
                    'keywords': keyword,
                    'page': '1',  # 这里不能给int类型的1，requests模块中可以
                    # 'time_from': '1537703217',
                    # 'time_to':'1569239217'
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
                item['source'] = ['网站', '500010000000004']
                item["title"] = str(doc_dict['title'])
                item["title"] = item["title"].replace('<em>','')
                item["title"] = item["title"].replace('</em>', '')
                item["title"] = item["title"].replace('<\\\\/em>', '')
                item["title"] = item["title"].replace('[', '')
                item["title"] = item["title"].replace(']', '')
                item["url"] = str(doc_dict['url']).replace('\\','')
                item["urlId"] = item["url"].split('post_')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
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