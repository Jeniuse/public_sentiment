# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 贵州省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcngz'
    allowed_domains = ['gbdsj.guizhou.gov.cn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://gbdsj.guizhou.gov.cn/search.html?keyword=%s'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        html = response.text
        html = str(html)
        docs = html.split("DOCPUBURL")[1:]
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for doc in docs:
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['source'] = ['网站', '500010000000004']
            url = doc.split(':\"', 1)[1].split('\"', 1)[0]
            doc = doc.split("DOCPUBTIME", 1)[1]
            creattime = doc.split(':\"',1)[1].split('\"',1)[0]
            doc = doc.split("DOCID", 1)[1]
            id = doc.split(':', 1)[1].split(',', 1)[0]
            doc = doc.split("DOCTITLE", 1)[1]
            title = doc.split(':\"',1)[1].split('\"',1)[0]
            title = title.replace('<em>','')
            title = title.replace('</em>','')
            item["title"] = title
            item["url"] = url
            item["urlId"] = '%s_%s' % (self.name, id)
            item["time"] = creattime.replace(' ','')[0:10]
            print(item["time"])
            if TimeMarch.time_March(item["time"], self.default_scope_day):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            res_child = child_page(item["url"])
            item["info"] = res_child.xpath("//font[@id='Zoom']/div/span/text() | //font[@id='Zoom']//span/text() | //font[@id='Zoom']//p/text()")
            item["info"] = "".join(item["info"])
            yield item
        if (len(docs)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keyword=')[1].split('&')[0]
            page_num = response.url.split('pageNumber=')[1].split('&')[0]
            page_num = int(page_num) + 1
            print('\n第***********************************%s***********************************页\n'%str(page_num))
            NextPageUrl = "http://gbdsj.guizhou.gov.cn/57/front/search.jhtml?code=c10a0a56f987453cb15e6a1fe45f7b8&keyword="+str(keyword)+"&pageNumber="+str(page_num)+"&filterParam=typename%3A1%3BsiteName%3A50&timeScope=+&orderBy=time&_=1569230227733"
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫