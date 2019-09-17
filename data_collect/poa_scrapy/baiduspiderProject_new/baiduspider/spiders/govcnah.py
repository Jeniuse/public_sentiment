# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnah'
    allowed_domains = ['gdj.ah.gov.cn']
    start_urls = [
        "http://gdj.ah.gov.cn/isearch.php?keytype=1&keycontent=%D6%B1%B2%A5%CE%C0%D0%C7&StartPage=0", #直播卫星
        "http://gdj.ah.gov.cn/isearch.php?keytype=1&keycontent=%B7%F6%C6%B6%B9%A4%D7%F7&StartPage=0", #中星九号
        "http://gdj.ah.gov.cn/isearch.php?keytype=1&keycontent=%D6%D0%D0%C7%BE%C5%BA%C5&StartPage=0"  #扶贫工程
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("/html/body/div[4]/div[3]/div")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = False
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                item["title"] = node.xpath("./a/text()").extract()
                item["url"] = node.xpath("./a/@href").extract_first()
                item["url"] = 'http://gdj.ah.gov.cn/%s'%item["url"]
                item["urlId"] = item["url"].split('id=')[-1]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                item["time"] = node.xpath("./p[2]/span[2]/text()").extract_first()
                # item["time"] = item["time"][0].split(' ')[0]
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                print(res_child)
                item["info"] = res_child.xpath("//div[@id = 'Zoom']/p/text() | //div[@id = 'Zoom']/p/font/text() | //div[@id = 'Zoom']/text() | //div[@id = 'Zoom']/font/text() | //div[@id = 'Zoom']/p/span/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False

            yield item
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keycontent=')[1].split('&')[0]
            page_num = response.url.split('StartPage=')[1]
            page_num = int(page_num)/15
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num) * 15 + 15
            NextPageUrl = "http://gdj.ah.gov.cn/isearch.php?keytype=1&keycontent=%s&StartPage=%s"%(str(page_num),keyword)
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫