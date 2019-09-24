# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山东省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnsd'
    allowed_domains = ['gd.shandong.gov.cn']
    start_urls = [
        "http://gd.shandong.gov.cn/gentleCMS/cmssearch/search.do?siteId=224c56cd-948a-4ac8-95bf-a44822be2f09&content=%s&currentpage=1"%"直播卫星",
        "http://gd.shandong.gov.cn/gentleCMS/cmssearch/search.do?siteId=224c56cd-948a-4ac8-95bf-a44822be2f09&content=%s&currentpage=1"%"中星九号",
        "http://gd.shandong.gov.cn/gentleCMS/cmssearch/search.do?siteId=224c56cd-948a-4ac8-95bf-a44822be2f09&content=%s&currentpage=1"%"扶贫工程"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//div[@align='left']")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        pagecount = 0
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["url"] = node.xpath("./a[1]/@href").extract_first()
                item["url"] = 'http://gd.shandong.gov.cn%s'%item["url"]
                item["urlId"] = item["url"].split('articles/')[-1].split('/')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./font[@class='filterTime']/text()").extract_first()
                item["time"] = "".join(item["time"])
                # item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y年%m月%d日"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["title"] = res_child.xpath("//h1[@class='title']/text() | //div[@class='editor-content editor-content-nweview']/p/text() | //div[@class='editor-content editor-content-nweview']/p/font/text() | //div[@class='editor-content editor-content-nweview']/p")
                item["info"] = res_child.xpath("//p[@class='MsoNormal']/span/text() | //font/text()  | //div[@class='editor-content editor-content-nweview']//p/text()")
                item["info"] = "".join(item["info"])
                pub_time = res_child.xpath("//div[@class='content content-view']/p[1]/span[1]/text()")
                if pub_time is not None:
                    item["time"] = pub_time
                    item["time"] = "".join(item["time"])
                    item["time"] = str(item["time"])[0:10]
                title = item["title"][0]
                item["title"] = title
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('content=')[1].split('&')[0]
            page_num = response.url.split('currentpage=')[-1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gd.shandong.gov.cn/gentleCMS/cmssearch/search.do?siteId=224c56cd-948a-4ac8-95bf-a44822be2f09&content=%s&currentpage=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            if page_num < 6:
                yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
            else:
                self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫