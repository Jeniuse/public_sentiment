# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from ..xml_filter import xml_filter
from .. import read_json
# 内蒙古广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnnmg'
    allowed_domains = ['gbdsj.nmg.gov.cn']
    start_urls = [
        "http://gbdsj.nmg.gov.cn/?m=search&c=index&a=init&typeid=1&siteid=1&q=%s&page=1"%"直播卫星",
        "http://gbdsj.nmg.gov.cn/?m=search&c=index&a=init&typeid=1&siteid=1&q=%s&page=1"%"中星九号",
        "http://gbdsj.nmg.gov.cn/?m=search&c=index&a=init&typeid=1&siteid=1&q=%s&page=1" % "扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//li[@class='wrap']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = node.xpath("./div/h5/a").extract()
                item["title"] = xml_filter("".join(item["title"]))
                item["url"] = node.xpath("./div/h5/a/@href").extract_first()
                item["urlId"] = item["url"].split('=')[-1]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item['info'] = node.xpath("//li[@class='wrap']/div/p").extract()
                item["info"] = xml_filter("".join(item["info"]))
                item["time"] = node.xpath("./div[@class='adds']/text()").extract_first()
                item["time"] = item["time"].split('：')[1]
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
            page_num = response.url.split('page=')[1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gbdsj.nmg.gov.cn/?m=search&c=index&a=init&typeid=1&siteid=1&q=%s&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
