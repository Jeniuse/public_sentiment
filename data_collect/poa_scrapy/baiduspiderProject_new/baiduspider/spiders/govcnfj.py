# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 福建省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnfj'
    allowed_domains = ['gdj.fujian.gov.cn']
    start_urls = [
        "http://gdj.fujian.gov.cn/was5/web/search?channelid=229105&templet=advsch.jsp&sortfield=-docreltime&classsql=%E7%9B%B4%E6%92%AD%E5%8D%AB%E6%98%9F*siteid%3D14&prepage=20&page=1",#"直播卫星",
        "http://gdj.fujian.gov.cn/was5/web/search?channelid=229105&templet=advsch.jsp&sortfield=-docreltime&classsql=%E4%B8%AD%E6%98%9F%E4%B9%9D%E5%8F%B7*siteid%3D14&prepage=20&page=1",#"中星九号",
        "http://gdj.fujian.gov.cn/was5/web/search?channelid=229105&templet=advsch.jsp&sortfield=-docreltime&classsql=%E6%89%B6%E8%B4%AB%E5%B7%A5%E7%A8%8B*siteid%3D14&prepage=20&page=1" #"扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        html = response.text
        html = str(html)
        docs = html.split("\"title\":\"")[1:-1]
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for doc in docs:
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            title = doc.split("\",")[0]
            doc = doc.split("\",", 1)[1].split('\"url\":\"')[1]
            url = doc.split("\",")[0]
            doc = doc.split("\",", 1)[1].split('\"time\":\"')[1]
            creattime = doc.split(' ')[0]
            item["title"] = title
            item["url"] = url
            item["urlId"] = item["url"].split('_')[-1].split('.')[0]
            item["urlId"] = '%s_%s' % (self.name, item["urlId"])
            item["time"] = creattime
            if TimeMarch.time_March(item["time"], self.default_scope_day):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            res_child = child_page(item["url"])
            item["info"] = res_child.xpath("//div[@class = 'Custom_UnionStyle']/p/text() | //div[@class = 'Custom_UnionStyle']/p/font/text() | //p/font/text() | //p/text()")
            item["info"] = "".join(item["info"])
            yield item
        if (len(docs) != 0) and (timecount < self.allowed_timesup):
            keyword = response.url.split('classsql=')[1].split('&')[0]
            page_num = response.url.split('&page=')[1]
            print('\n第***********************************%s***********************************页\n' % page_num)
            page_num = int(page_num) + 1
            NextPageUrl = "http://gdj.fujian.gov.cn/was5/web/search?channelid=229105&templet=advsch.jsp&sortfield=-docreltime&classsql=%s&prepage=20&page=%s" % (keyword, str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl, callback=self.parse, dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫
