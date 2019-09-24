# -*- coding: utf-8 -*-
import scrapy
import re
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 陕西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnshanx'
    allowed_domains = ['gdj.shaanxi.gov.cn']
    start_urls = [
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&keyword=55u05pKt5Y2r5pif",  #直播卫星
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&keyword=5Lit5pif5Lmd5Y%2B3",#中星九号
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&keyword=5om26LSr&"           #扶贫工程
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//div[@class='xwd']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:  # 分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["url"] = node.xpath("./div[1]/a/@href").extract_first()
                item["url"] = 'http://gdj.shaanxi.gov.cn/%s' % item["url"]
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./div[2]/text()").extract_first()
                item["time"] = "".join(item["time"])
                item["time"] = item["time"].split("时间：")[-1]
                # item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y年%m月%d日"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"], self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["title"] = res_child.xpath("//div[@class='article-title']/h1/text()")
                item["title"] = "".join(item["title"])
                item["info"] = res_child.xpath("//div[@class='v_news_content']/p/font/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keyword=')[1]
            page_num = response.url.split('currentnum=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=%s&keyword=%s"%(str(page_num),keyword)
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫