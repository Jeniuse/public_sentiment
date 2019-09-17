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
    name = 'govcnqh'
    allowed_domains = ['gdj.qinghai.gov.cn']
    start_urls = [
        "http://gdj.qinghai.gov.cn/index/yw/index.html",   #直播卫星",
        "http://gdj.qinghai.gov.cn/xingzhengzhifa/index.html", #中星九号",
        "http://gdj.qinghai.gov.cn/index/xw/index_5.html"  #扶贫"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//td[@class='ta']/table/tr")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = node.xpath("./td[2]/a/text()").extract_first()
                item["url"] = node.xpath("./td[2]/a/@href").extract_first()
                item["url"] = 'http://gdj.qinghai.gov.cn/%s'%item["url"]
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./td[3]/text()").extract_first()
                item["time"] = "".join(item["time"])
                # item["time"] = item["time"].split(' - ')[-1]
                # item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y年%m月%d日"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//p/span/text() | //p/font/span/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫
        # if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
        #     keyword = response.url.split('.cn/')[1].split('.html')[0].split('/')[0]
        #     page_num = response.url.split('p=')[1].split('&')[0]
        #     print('\n第***********************************%s***********************************页\n'%page_num)
        #     page_num = int(page_num)+1
        #     NextPageUrl = "http://www.zjxwcb.gov.cn/jsearch/search?q=%s&area=1&pos=1&date=1&p=%s&pg=10&x=17&y=13"%(keyword,str(page_num))
        #     print(NextPageUrl)
        #     yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        # else:
