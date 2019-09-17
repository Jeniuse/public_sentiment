# -*- coding: utf-8 -*-
import scrapy
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from .. import read_json
# 宁夏广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnnx'
    allowed_domains = ['gdj.nx.gov.cn']
    start_urls = [
        "http://gdj.nx.gov.cn/nzcms_list_so.asp?keyword=%D6%B1%B2%A5%CE%C0%D0%C7&so=3&Page=1", # 直播卫星
        "http://gdj.nx.gov.cn/nzcms_list_so.asp?keyword=%D6%D0%D0%C7%BE%C5%BA%C5&so=3&Page=1" # 中星九号
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//table/tr")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        print(len(nodelist))
        timecount = 0
        for node in nodelist:#分析帖子信息
            url = node.xpath("./td[2]/a/@href").extract_first()
            url = "http://gdj.nx.gov.cn/%s"%url
            ctime = node.xpath("./td[4]/text()").extract_first()
            if ctime!=None and '：' in ctime:
                ctime = ctime.split('：')[1]
                try:
                    # 判断这个帖子是否符合时间
                    ctime = time.strftime("%Y-%m-%d", time.strptime(ctime.split(' ')[0],"%Y年%m月%d日"))
                    if not TimeMarch.time_March(ctime,self.default_scope_day):
                        timecount = timecount + 1
                    if 'id=' in url:
                        yield scrapy.Request(url,callback = self.child_page)
                except:
                    url = ''
        if (len(nodelist)!=0) and (timecount<self.allowed_timesup):
            keyword = response.url.split('keyword=')[1].split('&')[0]
            page_num = response.url.split('Page=')[1]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.nx.gov.cn/nzcms_list_so.asp?keyword=%s&so=3&Page=%s"%(keyword,str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫
    def child_page(self, response):
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = False
        try:
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item["title"] = response.xpath("//tr/td/font/text()").extract_first()
            item["url"] = response.url
            item["urlId"] = item["url"].split('id=')[1]
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            item['time'] = response.xpath("//table[@class='dx']/tr/td/text()").extract_first()
            item['time'] = '%s日'%item['time'].split('发布时间：')[1].split('日')[0]
            item['info'] = response.xpath("//div/span/text() | //div/p/span/text()").extract()
            item["info"] = ("".join(item["info"])).replace('\xa0','').replace('\r\n','')
            try:
                # 判断这个帖子是否符合时间
                item['time'] = time.strftime("%Y-%m-%d", time.strptime(item['time'],"%Y年%m月%d日"))
                if TimeMarch.time_March(item['time'],self.default_scope_day):
                    item['IsFilter'] = True
            except:
                item['IsFilter'] = False
        except:
            item['IsFilter'] = False
        yield item
        
