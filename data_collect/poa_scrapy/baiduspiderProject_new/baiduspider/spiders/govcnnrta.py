# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 国家广播电视总局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnnrta'
    allowed_domains = ['www.nrta.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://www.nrta.gov.cn/jrobot/search.do?webid=1&analyzeType=1&pg=12&p=1&tpl=7&category=&q=%s'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//div[@class='jsearch-result-box']")#得到一页中的所有帖子
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
                item["title"] = node.xpath(".//div[@class='jsearch-result-title']/a/text()").extract_first()
                item["url"] = node.xpath(".//div[@class='jsearch-result-url']/a/text()").extract_first()
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath(".//span[@class='jsearch-result-date']/text()").extract_first()
                item["time"] = item["time"].split(' ')[0]
                item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0],"%Y年%m月%d日"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//p/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('q=')[1]
            page_num = response.url.split('p=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://www.nrta.gov.cn/jrobot/search.do?webid=1&pg=12&p=%s&tpl=&category=&q=%s"%(str(page_num),keyword)
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
