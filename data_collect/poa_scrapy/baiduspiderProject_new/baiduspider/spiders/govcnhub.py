# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 湖北省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnhub'
    allowed_domains = ['gdj.hubei.gov.cn']
    start_urls = [
        "http://gdj.hubei.gov.cn/gk/flfg/gfxwj/29758.htm"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        try:
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item["title"] = response.xpath("//div[@class='cont']/h2/text()").extract()
            item["title"] = "".join(item["title"])
            item["url"] = response.url
            item["urlId"] = item["url"].split('/')[-1].split('.')[0]
            item["urlId"] = '%s_%s' % (self.name, item["urlId"])
            item["time"] = response.xpath("//table[@class='s1']/tbody/tr[2]/td[2]/text()").extract_first()
            item["info"] = response.xpath("//p[@class='MsoNormal']/text()").extract()
            item["info"] = "".join(item["info"])
            # 判断这个帖子是否符合时间
            if TimeMarch.time_March(item["time"], self.default_scope_day):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
        except:
            item['IsFilter'] = False
        yield item
        self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫