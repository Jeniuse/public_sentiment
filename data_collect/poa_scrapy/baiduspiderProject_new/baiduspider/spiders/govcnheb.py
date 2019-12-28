# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 河北省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnheb'
    allowed_domains = ['old.hbcbgd.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://old.hbcbgd.gov.cn/?do=search_contents&name=%s&page=1'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//div[@class='content']/table/tr/td//table/tr/td/a")#得到一页中的所有帖子
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
                item["title"] = node.xpath("./text()").extract_first()
                item["url"] = node.xpath("./@href").extract_first()
                item["url"] = 'http://www.hbcbgd.gov.cn%s'%item["url"]
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                res_child = child_page(item["url"])
                # print(res_child.text)
                item["time"] = res_child.xpath("//div[@id='mainbox']/div[3]/text() | //div[@class='docDetail']/text() | //div[@class='docDetail']")
                # item["time"] = item["time"].split('局')[-1].split(' ')[-1]
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                item["info"] = res_child.xpath("//p/text()  | //div[@class='content'] | //div[@class='content']/p/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('name=')[1]
            page_num = response.url.split('page=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://www.hbcbgd.gov.cn/?do=search_contents&name=%s&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫