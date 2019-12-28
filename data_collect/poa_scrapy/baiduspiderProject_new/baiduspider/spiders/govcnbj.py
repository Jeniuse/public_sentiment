# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 北京市广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnbj'
    allowed_domains = ['gdj.beijing.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://gdj.beijing.gov.cn/so/s?qt=%s&siteCode=1100000109&tab=all&timeOption=1&days=60&sort=dateDesc&keyPlace=0&page=1'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//div[@class='msg discuss'] | ////div[@class='msg topic']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['source'] = ['网站', '500010000000004']
            item["title"] = node.xpath("./div[@class='titleP']/a/@title").extract_first()
            item["url"] = node.xpath("./div[@class='titleP']/a/@href").extract_first()
            item["url"] = 'http://so.kaipuyun.cn/%s'%item["url"]
            item["urlId"] = '12'
            item["time"] = node.xpath("./div[@class='content']/span/text() | .//span[@class='colo-666']/text()").extract_first()
            item["info"] = node.xpath("./div[@class='content']/p/text() | ./div[@class='content']/p/font/text()").extract()
            item["info"] = "".join(item["info"])
            try:
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    timecount = timecount + 1
            except:
                item['IsFilter'] = False
            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('qt=')[1].split('&')[0]
            page_num = response.url.split('page=')[1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.beijing.gov.cn/so/s?qt=%s&siteCode=1100000109&tab=all&timeOption=1&days=60&sort=dateDesc&keyPlace=0&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
