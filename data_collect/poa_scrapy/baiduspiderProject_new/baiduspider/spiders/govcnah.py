# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnah'
    allowed_domains = ['gdj.ah.gov.cn']
    with open('../keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://gdj.ah.gov.cn/site/search/49631961?keywords=%s&pageIndex=1&pageSize=10'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限

    def parse(self, response):
        nodelist = response.xpath("//ul[@class='search-list']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item['source'] = ['网站', '500010000000004']
                item["title"] = node.xpath("./li[@class='search-title']/a/text()").extract()
                item["title"] = "".join(item["title"])
                item["url"] = node.xpath("./li[@class='search-title']/a/@href").extract_first()
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("//span[@class='date']/text()").extract_first()

                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//div[@class = 'wzcon j-fontContent clearfix']/p/text() | //div[@class='con_main']//span/text() | //div[@id='wenzhang']//p/text() | //div[@class='con_main']//td/text() | //div[@class='desc']//span/text() | //div[@id = 'Zoom']/font/text() | //div[@id = 'Zoom']/p/span/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keywords=')[1].split('&')[0]
            page_num = response.url.split('pageIndex=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.ah.gov.cn/site/search/49631961?keywords=%s&pageIndex=%s&pageSize=10"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫