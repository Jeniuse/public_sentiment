# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 上海广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnsh'
    # allowed_domains = ['whlyj.sh.gov.cn']
    start_urls = [
        "http://searchgov1.eastday.com/searchwgj/search.ashx?q=%D6%B1%B2%A5%CE%C0%D0%C7&page=1",
        "http://searchgov1.eastday.com/searchwgj/search.ashx?q=%D6%D0%D0%C7%BE%C5%BA%C5&page=1"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//div[@id='items']/div[@class='resultItem']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item["title"] = node.xpath("./a/text()").extract()
            item["title"] = "".join(item["title"])
            item["url"] = node.xpath("./a/@href").extract_first()
            item["urlId"] = item["url"].split('/')[-1].split('.')[0]
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            item["info"] = node.xpath("./div/text()").extract()
            item["info"] = "".join(item["info"])
            item["time"] = node.xpath("./font/text()").extract_first()
            item["time"] = item["time"].split(' ')[1]
            try:
                item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0],"%Y年%m月%d日"))
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
            NextPageUrl = "http://searchgov1.eastday.com/searchwgj/search.ashx?q=%s&page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
