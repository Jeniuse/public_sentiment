# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 辽宁省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnln'
    allowed_domains = ['gdj.ln.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://www.ln.gov.cn/was5/web/search?page=1&channelid=267336&searchword=%s&perpage=10&outlinepage=10&searchscope=doctitle&timescope=&timescopecolumn=&orderby=&andsen=&total=&orsen=&exclude='%keyword)


    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//div[@class = 'search-news-mod']")#得到一页中的所有帖子
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
                item["title"] = node.xpath("./h1/a/text()").extract_first()
                item["url"] = node.xpath("./h1/a/@href").extract_first()
                item["urlId"] = item["url"].split('.')[0].split('/')[-1]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./p[2]/text()").extract_first()
                item["time"] = item["time"].split('时间：')[-1].split(' ')[0]
                item["time"] = item["time"].replace('.','-')
                item["info"] = node.xpath("./p[1]/text()").extract_first()
                # item["info"] = node.xpath("./p[1]/text()").extract_first()
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
            except:
                item['IsFilter'] = False
            yield item
        self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫
        # if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
        #     keyword = response.url.split('title=')[1]
        #     page_num = response.url.split('p=')[1].split('&')[0]
        #     print('\n第***********************************%s***********************************页\n'%page_num)
        #     page_num = int(page_num)+1
        #     NextPageUrl = "http://gdj.shanxi.gov.cn/soso.aspx?p=%s&title=%s&type=1"%(str(page_num),keyword)
        #     print(NextPageUrl)
        #     yield scrapy.Request(NextPageUrl,callback = self.parse)
        # else:
