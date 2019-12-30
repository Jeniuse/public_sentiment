# -*- coding: utf-8 -*-
import scrapy
import time
import json
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 宁夏省广播电视局
# 6分钟
class hhtcsSpider(scrapy.Spider):
    name = 'govcnnx2'
    allowed_domains = ['gdj.nx.gov.cnn']
    with open('./keywords.txt', 'r', encoding='utf8') as fp:
        keywords = json.loads(fp.read())
    start_urls = []
    for keyword in keywords:
        start_urls.append('http://gdj.nx.gov.cn/was5/web/search?searchword=%s&channelid=244757&page=1'%keyword)

    allowed_timesup = 10  # 最多超过时限次数
    default_scope_day = 60 #首次爬取时限


    def parse(self, response):
        nodelist = response.xpath("//div[@class='wr_body_type1 cont2']//li")#得到一页中的所有帖子
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
                item["url"] = node.xpath("./a/@href").extract_first()
                item["urlId"] = item["url"].split('_')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["title"] = node.xpath("./a/text()").extract_first()
                # item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y年%m月%d日"))
                res_child = child_page(item["url"])
                item["info"] = res_child.xpath("//div[@id = 'z']/p//span/text() |//div[@id = 'z']//p/text()")
                item["info"] = "".join(item["info"])
                item["info"] = item["info"][0:2000]
                item["time"] = res_child.xpath("//td[@align='center']/span/text()")
                item["time"] = "".join(item["time"])
                item["time"] = item["time"].split('：')[-1]
                item["time"] = item["time"].replace('年','-')
                item["time"] = item["time"].replace('月', '-')
                item["time"] = item["time"].replace('日', '')
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"], self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('searchword=')[1].split('&')[0]
            page_num = response.url.split('page=')[1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.nx.gov.cn/was5/web/search?searchword=%s&channelid=244757&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫