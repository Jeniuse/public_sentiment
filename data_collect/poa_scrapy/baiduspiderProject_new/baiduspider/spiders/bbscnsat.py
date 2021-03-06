# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 卫星电视论坛
class hhtcsSpider(scrapy.Spider):
    name = 'bbscnsat'
    allowed_domains = ['bbs.cnsat.net']
    start_urls = [
        "http://bbs.cnsat.net/forum-32-1.html"
    ]
    page_num = 1 # 页码
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//div[@class='jsearch-result-box']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = True
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            item["title"] = node.xpath("./div[@class='jsearch-result-title']/a/text()").extract_first()
            item["url"] = node.xpath("./div/div/div[@class='jsearch-result-url']/a/text()").extract_first()
            item["urlId"] = item["url"].split('/')[-1].split('.')[0]
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            item["time"] = node.xpath("./div/div/span[@class='jsearch-result-date']/text()").extract_first()
            item["time"] = item["time"].split(' ')[0]
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
            res_child = child_page(item["url"])
            item["info"] = res_child.xpath("//p/text()")
            item["info"] = "".join(item["info"])
            yield item
        print('\n第***********************************%d***********************************页\n'%self.page_num)
        self.page_num = self.page_num + 1
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('q=')[1]
            print(keyword)
            NextPageUrl = "http://www.nrta.gov.cn/jrobot/search.do?webid=1&pg=12&p=%s&tpl=&category=&q=%s"%(str(self.page_num),keyword)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
