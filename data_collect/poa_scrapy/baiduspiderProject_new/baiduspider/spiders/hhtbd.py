# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'hhtbd'
    allowed_domains = ['www.huhutong315.com']
    start_urls = [
        "http://www.huhutong315.com/dz_beidougaoqing/"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//dl[@class = 'bbda cl']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item["title"] = node.xpath("./dt/a/text()").extract_first()
            item["url"] = node.xpath("./dt/a/@href").extract_first()
            item["urlId"] = item["url"].split('/')[-1].split('.')[0]
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            item["time"] = node.xpath("./dd[2]/span/text()").extract_first()
            item["time"] = item["time"].split(' ',1)[-1]

            try:
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
            except:
                item['IsFilter'] = False
            res_child = child_page(item["url"])
            item["info"] = res_child.xpath("//td[@id='article_content']/p/span/text() | //td[@id='article_content']/font/text() | //td[@id='article_content']/p/text() | //td[@id='article_content']/div/span/text() | //td[@id='article_content']/span/text()")
            item["info"] = "".join(item["info"])
            item["comment"] = res_child.xpath("//p[@class='xg1']/a[2]/em/text()")
            item["latestcomtime"] = res_child.xpath("//div[@class='bm_c']/dl[1]/dt/span[@class='xg1 xw0']/text()")
            item["latestcomtime"] = "".join(item["latestcomtime"])
            if item["latestcomtime"] == "":
                item["latestcomtime"] = None
            if item["comment"] != []:
                item["comment"] = item["comment"][0]
            else:
                item["comment"] = None
            item["read"] = res_child.xpath("//em[@id='_viewnum']/text()")[0]
            yield item
        self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫