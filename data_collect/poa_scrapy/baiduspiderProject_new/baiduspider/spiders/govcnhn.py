# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 湖南省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnhn'
    allowed_domains = ['gbdsj.hunan.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://searchs.hunan.gov.cn/hunan/gbdsj/news?q=%s&searchfields=&sm=0&columnCN=&p=0&timetype=timeqb'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//li[@class='active']")#得到一页中的所有帖子
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
                item["url"] = node.xpath("./div[@class='com-title']/a/@href").extract_first()
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./div[2]/div/span[2]/text()").extract_first()
                item["time"] = item["time"].split('：')[-1]
                res_child = child_page(item["url"])
                # item["info"] = res_child.xpath("//div[@id='j-show-body']/div/div/p/span/voice/text()")
                item["info"] = res_child.xpath("//span/text()")
                item["info"] = "".join(item["info"])
                item["title"] = res_child.xpath("//div[@class='main_content']/h2/text()")
                item["title"] = "".join(item["title"])
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
            except:
                item['IsFilter'] = False
            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('q=')[1].split('&')[0]
            page_num = response.url.split('p=')[1].split('&')[0]
            page_num = int(page_num)
            print('\n第***********************************%s***********************************页\n' % (page_num + 1))
            page_num = page_num + 1
            NextPageUrl = "http://searchs.hunan.gov.cn/hunan/gbdsj/news?q=%s&searchfields=&sm=0&columnCN=&p=%s&timetype=timeqb" % (
            keyword, str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl, callback=self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫