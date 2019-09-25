# -*- coding: utf-8 -*-
import scrapy
from baiduspider.items import BaiduspiderItem
from baiduspider.items import inititem
from .. import TimeCalculate
from .. import TimeMarch
from .. import ChildPage
from .. import read_json
from .. import read_file
import time

class wszgcsSpider(scrapy.Spider):
    name = 'wszg'
    allowed_domains = ['www.wszgw.net']
    start_urls = [
        "https://www.wszgw.net/forum.php?mod=forumdisplay&fid=232",
        "https://www.wszgw.net/forum-296-1.html",
        "https://www.wszgw.net/forum-232-1.html",
        "https://www.wszgw.net/forum-203-1.html",
        "https://www.wszgw.net/forum-235-1.html"
    ]
    idlist = read_file.read_file(name)
    allowed_timesup = 10  # 最多超过时限次数
    if (read_json.read_json(name)):
        default_scope_day = 50  # 首次爬取时限
    else:
        default_scope_day = 30  # 增量爬取时限

    def parse(self, response):
        nodelist = response.xpath('//tbody/tr')#得到一页中的所有帖子
        item = BaiduspiderItem()
        item = inititem(item)
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息
            #首判断是否符合时间限制
            item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item["time"] = node.xpath('./th/a[2]/../../td[2]/em//text()').extract_first()
            # 处理时间为空的情况
            if item["time"] == None:
                item["time"]=''
            item["time"] = item["time"].strip()
            item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
            if (TimeMarch.time_March(item["time"], self.default_scope_day) == True):
                item["IsFilter"] = True
            else:
                item["IsFilter"] = False
                timecount = timecount + 1
            item["title"] = node.xpath("./th/a[2][@class='s xst']/text()").extract_first()
            item["url"] = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
            item["read"] = node.xpath("./td[3][@class='num']/em/text()").extract_first()
            item["comment"] = node.xpath("./td[3][@class='num']/a/text()").extract_first()
            item["latestcomtime"] = node.xpath("./td[4]/em/a/text() | ./td[4]/em/a/span/@title").extract_first()
            if(item["IsFilter"] == True):#如果符合时间限制的话
                childUrl = node.xpath("./th/a[2][@class='s xst']/@href").extract_first()
                if (childUrl != None):#判断是否已经爬过,决定是否访问子页面
                    id = item['url'].split('/')[3]  # 得到url
                    num = id.split('-')[1]
                    item["info"] = ChildPage.ChildPage(childUrl, '3')

            if(NextPageUrl == ''):#记录下一页的链接
                NextPageUrl =response.xpath('//a[@class="bm_h"]/@rel').extract_first()
            if item["url"] != None:  # 非普通帖子的错误处理（置顶帖等异常的帖子）
                item['urlId'] = item['url'].split('/')[3].split('-')[1]  # 得到urlId
                item["urlId"] = '%s_%s'%(self.name,item["urlId"])
                yield item #返回数据到pipeline
        if(timecount>self.allowed_timesup or NextPageUrl==None):#根据判断决定继续爬取还是结束
            #结束爬取
            item = BaiduspiderItem()
            item["IsFilter"]=False
            yield item
        else:
            yield scrapy.Request('https://www.wszgw.net/'+NextPageUrl,callback = self.parse)
