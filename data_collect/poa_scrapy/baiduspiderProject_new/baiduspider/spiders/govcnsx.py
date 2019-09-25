# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnsx'
    allowed_domains = ['gdj.shanxi.gov.cn']
    start_urls = [
        "http://gdj.shanxi.gov.cn/soso.aspx?p=1&title=%s&type=1"%"直播卫星",
        "http://gdj.shanxi.gov.cn/soso.aspx?p=1&title=%s&type=1"%"中星九号",
        "http://gdj.shanxi.gov.cn/soso.aspx?p=1&title=%s&type=1"%"扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//span[@class = 'list plist rc']/a")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = node.xpath("./text()").extract_first()
                item["url"] = node.xpath("./@href").extract_first()
                item["url"] = 'http://gdj.shanxi.gov.cn/%s'%item["url"]
                item["urlId"] = item["url"].split('id=')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./em/text()").extract_first()
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//div[@id = 'Zoom']/p/text() | //div[@id='Zoom']/text()")
                item["info"] = "".join(item["info"])
                # item["info"] = bytearray.fromhex(''.join(item["info"].split("\\x"))).decode()
            except:
                item['IsFilter'] = False
            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('title=')[1]
            page_num = response.url.split('p=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.shanxi.gov.cn/soso.aspx?p=%s&title=%s&type=1"%(str(page_num),keyword)
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫