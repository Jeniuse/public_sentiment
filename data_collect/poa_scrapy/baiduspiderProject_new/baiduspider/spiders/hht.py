# -*- coding: utf-8 -*-
import scrapy
import datetime
import  time
from baiduspider.items import BaiduspiderItem
from .. import TimeCalculate
from .. import TimeMarch
from .. import ChildPage
from .. import read_json

class hhtcsSpider(scrapy.Spider):
    name = 'hht'
    allowed_domains = ['www.huhutong315.com']
    start_urls = [
        "http://www.huhutong315.com/forum-94-1.html",
        "http://www.huhutong315.com/forum-93-1.html",
        "http://www.huhutong315.com/forum-92-1.html",
        "http://www.huhutong315.com/forum-2-1.html",
        "http://www.huhutong315.com/forum-103-1.html"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 50 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath('//tbody/tr')#得到一页中的所有帖子
        item = BaiduspiderItem()
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            childUrl = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
            item["title"]= node.xpath("./th/a[2][@class='s xst']/text()").extract_first()
            item["url"] = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
            item["comment"] = node.xpath("./td[@class='num']/a/text()").extract_first()
            item["read"] = node.xpath("./td[@class='num']/em/text()").extract_first()
            item["latestcomtime"] = node.xpath("./td[4]/em/a/span/@title | ./td[4]/em/a/text()").extract_first()
            if(childUrl != None):
                item["info"] = ChildPage.ChildPage(childUrl,'1')
            item["time"] = node.xpath('./th/a[2]/../../td[@class="by"]/em/span/text()').extract_first()
            if item["time"] == None:
                item["time"] = node.xpath('./th/a[2]/../../td[@class="by"]/em/span/span/text()').extract_first()
            #处理时间为空的情况
            if item["time"] == None:
                item["time"] = ''
            else:
                item["time"] = item["time"].strip()
                item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
            # # 处理简介为空的情况
            # if item["info"] == None:
            #     item["info"] = ''
            # 判断这个帖子是否符合时间
            if(TimeMarch.time_March(item["time"],self.default_scope_day)==True):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            if(NextPageUrl == ''):#记录下一页的链接
                NextPageUrl =response.xpath('//a[@class="bm_h"]/@rel').extract_first()
            if item["url"] != None:  # 非普通帖子的错误处理（置顶帖等异常的帖子）
                item['urlId'] = item['url'].split('/')[3].split('-')[1]  # 得到urlId
                item["urlId"] = '%s_%s'%(self.name,item["urlId"])
                yield item #返回数据到pipeline
        if(timecount>self.allowed_timesup or NextPageUrl==None):#根据判断决定继续爬取还是结束
            #结束爬取
            item = BaiduspiderItem()
            item["IsFilter"]=False
            yield item
        else:
            yield scrapy.Request('http://www.huhutong315.com/'+NextPageUrl,callback = self.parse)
