# -*- coding: utf-8 -*-
import scrapy
from .. import read_json
import datetime
import os
from baiduspider.items import BaiduspiderItem
from .. import TimeCalculate
from .. import TimeMarch

class SimpleBaiduSpider(scrapy.Spider):
    name = 'baidu'
    keyword = '户户通'
    default_scope_day = 365  # 爬取时限(日)
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/f?kw='+keyword]
    if(read_json.read_json(name)):
        default_scope_day = 50 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath('//div[@class="col2_right j_threadlist_li_right "]')#得到一页中的所有帖子
        item = BaiduspiderItem()
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        for node in nodelist:#分析帖子信息
            item["title"]= node.xpath("./div[1]/div/a[@title]/text()").extract_first()
            item["url"] = node.xpath("./div[1]/div/a[@href]/@href").extract_first()
            item["info"] = node.xpath('./div[2]/div[@class="threadlist_text pull_left"]/div[1]/text()').extract_first()
            item["time"] = node.xpath('./div[1]/div[2]/span[@title="创建时间"]/text()').extract_first()
            item["time"] = item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
            # 判断一页中是否有符合年限的帖子
            if(isHasContent == False):
                isHasContent = TimeMarch.time_March(item["time"],self.default_scope_day)
            # 判断这个帖子是否符合时间
            if(TimeMarch.time_March(item["time"],self.default_scope_day)==True):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
            # 拼接子url
            childUrl = "https://tieba.baidu.com" + item["url"]
            item["url"] = childUrl
            item["urlId"] = item['url'].split('/')[4] #得到urlId
            item["urlId"] = '%s_%s'%(self.name,item["urlId"])
            # 处理简介为空的情况
            if item["info"] == None:
                item["info"]= ''
            else:
                item["info"]=item["info"].strip()#将多余空格去掉
            item["time"] = item["time"].strip()
            try:
                if (NextPageUrl == ''):  # 记录下一页的链接
                    NextPageUrl = 'https:' + response.xpath('//a[@class = "next pagination-item "]/@href').extract_first()
            except:
                url = response.url
                print("url is :----------"+url)
                temp = url.split("kw=")[1]
                if ("page" not in url):
                    NextPageUrl = "https://tieba.baidu.com/f?kw=" + keyword + "&ie=utf-8&pn=50"
                else:
                    page = temp.split("pn=")[1]
                    page = int(page)+50
                    NextPageUrl = "https://tieba.baidu.com/f?kw=" + keyword + "&ie=utf-8&pn="+str(page)

            yield item #返回数据到pipeline
        if(isHasContent==False):#根据判断决定继续爬取还是结束
             self.crawler.engine.close_spider(self, 'Finished')#关闭爬虫
        else:
            yield scrapy.Request(NextPageUrl,callback = self.parse)
            print("翻页了！！！！！！！！！！！！！！！！！\n\n\n")
