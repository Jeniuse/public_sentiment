# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 吉林省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnjl'
    allowed_domains = ['gdj.jl.gov.cn']
    with open('../keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://was.jl.gov.cn/was5/web/search?presearchword=&searchword1=&channelid=193132&StringEncoding=UTF-8&searchword=%s&page=1'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//td[@class = 'td_left30_right30']/table/tr/td")#得到一页中的所有帖子
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
                item["title"] = node.xpath("./span[@class = 'blue14bold']/a/text()").extract_first()
                item["url"] = node.xpath("./span[@class = 'blue14bold']/a/@href").extract_first()
                item["urlId"] = item["url"].split('_')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./span[@class = 'black12bold']/text()").extract_first()
                item["time"] = item["time"].split(' ')[1].split('\n')[0]  # 换行符表示
                item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y.%m.%d"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//div[@class='cas_content']//p/text() | //div[@class='submain']//span/text()| //div[@class='Custom_UnionStyle']//p/text() | //div[@class='Custom_UnionStyle']//span/p/text() |//div[@class='TRS_Editor']//p/text() | //div[@class='Custom_UnionStyle']//span/text()")  # 格式不统一
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False
            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('searchword=')[1].split('&')[0]
            page_num = response.url.split('page=')[-1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://was.jl.gov.cn/was5/web/search?presearchword=&searchword1=&channelid=193132&StringEncoding=UTF-8&searchword=%s&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫