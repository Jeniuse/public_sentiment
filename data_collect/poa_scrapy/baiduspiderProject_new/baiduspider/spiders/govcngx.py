# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 广西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcngx'
    allowed_domains = ['gbdsj.gxzf.gov.cn']
    start_urls = [
        "http://gbdsj.gxzf.gov.cn/index.php?m=search&c=index&a=init&page=2"
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//ul[@class='search_list']/li")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        item = inititem(item)
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = node.xpath("./a/text()").extract_first()
                item["url"] = node.xpath("./a/@href").extract_first()
                item["urlId"] = item["url"].split('/')[-1].split('.')[0]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                res_child = child_page(item["url"])
                item["time"] = node.xpath("./span/text()").extract_first()
                item["time"] = item["time"].replace('[','')
                item["time"] = item["time"].replace(']', '')
                # item["time"] = item["time"].split('局')[-1].split(' ')[-1]
                # 判断这个帖子是否符合时间
                if "直播卫星" in item["title"] or "中星九号" in item["title"] or "扶贫工程" in item["title"] or "扶贫" in item["title"]:
                    if TimeMarch.time_March(item["time"],self.default_scope_day):
                        item["IsFilter"] = True
                    else:
                        item["IsFilter"] = False
                        timecount = timecount + 1
                    res_child = child_page(item["url"])
                    print(res_child.text)
                    item["info"] = res_child.xpath("//div[@class='content content_article']/text()  | //div[@class='content content_article']/div/text()")
                    item["info"] = "".join(item["info"])
                    yield item
                else:
                    yield None
            except:
                i = 0
                yield None
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            page_num = response.url.split('page=')[1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            if page_num < 30:
                NextPageUrl = "http://gbdsj.gxzf.gov.cn/index.php?m=search&c=index&a=init&page=%s"%(str(page_num))
                print(NextPageUrl)
                yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫