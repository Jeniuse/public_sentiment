# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 四川省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnsc'
    allowed_domains = ['gdj.sc.gov.cn']
    start_urls = [
        "http://gdj.sc.gov.cn/scxwcbjss/search?keyword=%s&pageIndex=0"%"直播卫星",
        "http://gdj.sc.gov.cn/scxwcbjss/search?keyword=%s&pageIndex=0"%"中星九号",
        "http://gdj.sc.gov.cn/scxwcbjss/search?keyword=%s&pageIndex=0"%"扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        html = response.text
        html = str(html)
        docs = html.split("documentId")[1:]
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for doc in docs:
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            id = doc.split(':',1)[1].split(',',1)[0]
            doc = doc.split("documentDate", 1)[1]
            creattime = doc.split(':\"',1)[1].split('\"',1)[0]
            doc = doc.split("documentTitle", 1)[1]
            title = doc.split(':\"',1)[1].split('\",',1)[0]
            doc = doc.split("documentUrl", 1)[1]
            url = doc.split(':\"',1)[1].split('\"',1)[0]
            url = url.split("xwcbj2016")[1]
            url = "http://gdj.sc.gov.cn%s"%url
            item["title"] = title
            item["url"] = url
            item["urlId"] = '%s_%s' % (self.name, id)
            item["time"] = creattime.replace(' ','')
            if TimeMarch.time_March(item["time"], self.default_scope_day):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            res_child = child_page(item["url"])
            item["info"] = res_child.xpath("//div[@class = 'Custom_UnionStyle']/p/text() | //div[@class = 'Custom_UnionStyle']/p/font/text() | //div[@class='content']//span/text() | //div[@class='content']//font/text() | //div[@class = 'Custom_UnionStyle']//span/text()")
            item["info"] = "".join(item["info"])
            yield item
        if (len(docs)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keyword=')[1].split('&')[0]
            page_num = response.url.split('pageIndex=')[1]
            page_num = int(page_num) + 1
            print('\n第***********************************%s***********************************页\n'%str(page_num))
            NextPageUrl = "http://gdj.sc.gov.cn/scxwcbjss/search?keyword=%s&pageIndex=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫