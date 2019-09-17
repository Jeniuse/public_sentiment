# -*- coding: utf-8 -*-
import scrapy
import re
import time
from baiduspider.items import BaiduspiderItem
from .. import TimeMarch
from ..child_page import child_page
from .. import read_json
# 山西省广播电视局
class hhtcsSpider(scrapy.Spider):
    name = 'govcnshanx'
    allowed_domains = ['gdj.shaanxi.gov.cn']
    start_urls = [
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&newskeycode2=55u05pKt5Y2r5pif",  #直播卫星
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&newskeycode2=5Lit5pif5Lmd5Y%2B3",#中星九号
        "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=1&newskeycode2=5om26LSr"           #扶贫工程
    ]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 60 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        nodelist = response.xpath("//form[@id='searchlistform1']/table[1]/tbody/tr")#得到一页中的所有帖子
        nodelist = [] if nodelist==None else nodelist
        item = BaiduspiderItem()
        # 是否符合爬取条件
        item['IsFilter'] = False
        pagelist = None
        pagelist = response.xpath("//form[@id='searchlistform1']/table[2]/tbody/tr/td").extract_first()#得到搜索结果所有帖子数量
        pagenum = None
        currentnum = None
        if pagelist is not None:
            pagenum = re.findall('(\d+)',pagelist)[1]    #总共页数
            currentnum = re.findall('(\d+)',pagelist)[2] #当前页数
        timecount = 0  # 计数器
        i = 0
        for node in nodelist:#分析帖子信息
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                if i % 3 == 0:
                    i += 1
                    # item["title"] = node.xpath("./text()").extract_first()
                    item["url"] = node.xpath("./td/a/@href").extract_first()
                    item["urlId"] = item["url"].split('id=')[-1]
                    item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                if i % 3 == 2:
                    i += 1
                    item["time"] = node.xpath("./td/span/text()").extract_first()
                    item["time"] = item["time"][0].split('：')[1]
                item["time"] = time.strftime("%Y-%m-%d", time.strptime(item["time"].split(' ')[0], "%Y年%m月%d日"))
                # 判断这个帖子是否符合时间
                if TimeMarch.time_March(item["time"],self.default_scope_day):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1
                res_child = child_page(item["url"])
                item["title"] = res_child.xpath("//table[class = 'bk_3bh']/tbody/tr/td/form/div/h1/text()")
                item["info"] = res_child.xpath("//dive[class = 'v_news_content']/p/text()")
                item["info"] = "".join(item["info"])
            except:
                item['IsFilter'] = False
            yield item
        if pagenum != currentnum and pagelist is not None:
            keyword = response.url.split('newskeycode2=')[1]
            page_num = response.url.split('currentnum=')[1].split('&')[0]
            print('\n第***********************************%s***********************************页\n'%page_num)
            page_num = int(page_num)+1
            NextPageUrl = "http://gdj.shaanxi.gov.cn/chaxunjieguo.jsp?wbtreeid=1001&searchScope=0&currentnum=%s&newskeycode2=%s"%(str(page_num),keyword)
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished') # 关闭爬虫