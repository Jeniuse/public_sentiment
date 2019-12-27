# -*- coding: utf-8 -*-
import scrapy
import requests
from lxml import etree
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 国家广播电视总局
class hhtcsSpider(scrapy.Spider):
    name = 'lcdhome'
    allowed_domains = ['bbs.lcdhome.net']
    start_urls = [
        "http://bbs.lcdhome.net/thread-htm-fid-75.html"
    ]
    page_num = 1 # 页码
    page_all_num = 1
    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//tbody/tr[@class='tr3']")#得到一页中的所有帖子
        if self.page_all_num==1:
            pages = response.xpath("//div[@class='pages']")[0].xpath("./div[@class='fl']/text()").extract_first()
            self.page_all_num = int(pages[1:-1])
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['source'] = ['论坛', '500010000000001']
            item["title"] = node.xpath("./td[@class='subject']/a/b/font/text() | ./td[@class='subject']/a/text()").extract_first()
            item["url"] = node.xpath("./td[@class='subject']/a/@href").extract_first()
            item["urlId"] = item["url"].split('-')[-1].split('.')[0]
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            item["url"] = 'http://bbs.lcdhome.net/%s'%item["url"]
            item["time"] = node.xpath("./td[@class='author'][1]/p/text()").extract_first()
            item["read"] = node.xpath("./td[@class='num']/text()").extract_first()
            item["comment"] = node.xpath("./td[@class='num']/em/text()").extract_first()
            item["read"] = item["read"].split('/')[-1]
            item["latestcomtime"] = node.xpath("./td[5]/a/@title").extract_first()
            if item["read"] == "\xa0":
                item["read"] = None
            try:
                reply = int(item["read"])
            except:
                reply = 0
            try:
                if reply>=1000 and item["time"] != None:
                    # 判断这个帖子是否符合时间
                    if TimeMarch.time_March(item["time"],self.default_scope_day):
                        item["IsFilter"] = True
                    else:
                        item["IsFilter"] = False
                        timecount = timecount + 1
            except:
                item['IsFilter'] = False
            res_child = child_page(item["url"])
            xpath_info = "//div[@class='tpc_content']/div//font/text() | //div[@class='tpc_content']/div/text()"
            item["info"] = res_child.xpath(xpath_info) if res_child!=None else []
            item["info"] = item["info"][0].replace('\n','') if len(item["info"]) != 0 else ""
            yield item
        print('\n第***********************************%d***********************************页\n'%self.page_num)
        self.page_num = self.page_num + 1
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup) and (self.page_num<=self.page_all_num):
            NextPageUrl = "http://bbs.lcdhome.net/thread-htm-fid-75-page-%s.html"%str(self.page_num)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
