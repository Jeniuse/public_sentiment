# -*- coding: utf-8 -*-
import scrapy
import time
import datetime
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeCalculate
from .. import TimeMarch
from .. import ChildPage
from .. import read_json

class jdwxbzSpider(scrapy.Spider):
    name = 'jdwx'
    allowed_domains = ['www.jdwx.info']
    start_urls = [
        'http://www.jdwx.info/forum-26-1.html',
        'http://www.jdwx.info/forum-29-1.html'
    ]
    allowed_timesup = 10 #最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath('//tbody/tr')#得到一页中的所有帖子
        item = BaiduspiderItem()
        item = inititem(item)
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息\
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['source'] = ['论坛', '500010000000001']
            childUrl = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
            item["title"]= node.xpath("./th/a[2][@class='s xst']/text()").extract_first()
            item["url"] = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
            item["read"] = node.xpath("./td[3][@class='num']/em/text()").extract_first()
            item["comment"] = node.xpath("./td[3][@class='num']/a/text()").extract_first()
            item["latestcomtime"] = node.xpath("//tbody/tr/td[4]/em/a/span/@title | //tbody/tr/td[4]/em/a/text()").extract_first()
            if (childUrl != None):
                item["info"] = ChildPage.ChildPage(childUrl,'2')
            item["time"] = node.xpath('./th/a[2]/../../td[@class="by"]/em/span/text()').extract_first()

            if item["time"] == None:
                item["time"] = node.xpath('./th/a[2]/../../td[@class="by"]/em/span/span/text()').extract_first()
            #处理时间为空的情况
            if item["time"] == None:
                item["time"] = ''
            else:
                item["time"] = item["time"].strip()
                item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
            # 判断这个帖子是否符合时间
            if(TimeMarch.time_March(item["time"],self.default_scope_day)==True):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            if(NextPageUrl == ''):#记录下一页的链接
                NextPageUrl = response.xpath('//div[@class="pg"]/a[@class="nxt"]/@href').extract_first()
            if item["url"] != None:  # 非普通帖子的错误处理（置顶帖等异常的帖子）
                item['urlId'] = item['url'].split('/')[3].split('-')[1]  # 得到urlId
                item["urlId"] = '%s_%s'%(self.name,item["urlId"])
                yield item #返回数据到pipeline
        if(timecount>self.allowed_timesup):#根据判断决定继续爬取还是结束
             self.crawler.engine.close_spider(self, 'Finished')#关闭爬虫
        else:
            yield scrapy.Request(NextPageUrl,callback = self.parse)
