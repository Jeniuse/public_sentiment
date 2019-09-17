# -*- coding: utf-8 -*-
import scrapy
import time
from .. import read_json
import datetime
import os
from baiduspider.items import BaiduspiderItem
from ..child_page import child_page
from .. import TimeCalculate
from .. import TimeMarch

class SimpleBaiduSpider(scrapy.Spider):
    name = 'baidu'
    keyword = '户户通'
    default_scope_day = 365  # 爬取时限(日)
    allowed_domains = ['tieba.baidu.com']
    start_urls = ['https://tieba.baidu.com/f?kw=%s&ie=utf-8&pn=0'%keyword]
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 50 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限

    def parse(self, response):
        timecount = 0  # 计数器
        html = str(response.text)
        docs = html.split("t_con cleafix")[2:]
        item = BaiduspiderItem()
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        for doc in docs:
            try:
                item['spidertime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                doc = doc.split("回复",1)[1]
                item["comment"] = doc.split('>',1)[1].split('<',1)[0]
                url = doc.split("href=\"",1)[1].split('\"',1)[0]
                item["url"] = "https://tieba.baidu.com%s" % url
                item["urlId"] = item["url"].split('/')[-1]
                item["urlId"] = '%s_%s' % (self.name, item["urlId"])
                doc = doc.split("href=\"",1)[1].split('\"',1)[1]
                title = doc.split("title=\"")[1].split('\"',1)[0]
                item["title"] = title
                doc = doc.split("创建时间",1)[1]
                creattime = doc.split("\">", 1)[1].split('<', 1)[0]
                item["time"] = "2019-%s"%creattime
                doc = doc.split("threadlist_abs threadlist_abs_onlyline", 1)[1]
                item["info"] = doc.split('>',1)[1].split('</div>',1)[0]
                doc = doc.split("最后回复时间", 1)[1]
                reply = doc.split("\">", 1)[1].split('<', 1)[0]
                reply = reply.replace(' ', '')
                reply = reply.replace('\n', '')
                reply = reply.replace('\r', '')
                if '-' in reply:
                    item["latestcomtime"] = '2019-%s' % reply
                else:
                    reply = str(time.strftime('%Y-%m-%d',time.localtime(time.time())))+' '+reply
                    item["latestcomtime"] = reply

                # 判断一页中是否有符合年限的帖子
                if (isHasContent == False):
                    isHasContent = TimeMarch.time_March(item["time"], self.default_scope_day)
                # 判断这个帖子是否符合时间
                if (TimeMarch.time_March(item["time"], self.default_scope_day) == True):
                    item["IsFilter"] = True
                else:
                    item["IsFilter"] = False
                    timecount = timecount + 1

                # 处理简介为空的情况
                if item["info"] == None:
                    item["info"] = ''
                else:
                    item["info"] = item["info"].strip()  # 将多余空格去掉
                item["time"] = item["time"].strip()
            except:
                print()
            yield item  # 返回数据到pipeline
        if (len(docs) != 0) and (timecount < self.allowed_timesup):
            keyword = response.url.split('kw=')[1].split('&')[0]
            page_num = response.url.split('&pn=')[1]
            page_num = int(page_num)/50 + 1
            print('\n第***********************************%s***********************************页\n' % str(page_num))
            page_num = int(page_num) * 50
            NextPageUrl = 'https://tieba.baidu.com/f?kw=%s&ie=utf-8&pn=%s' % (keyword, str(page_num))
            print(NextPageUrl)
            yield scrapy.Request(NextPageUrl, callback=self.parse, dont_filter=True)
        else:
            self.crawler.engine.close_spider(self, 'Finished')  # 关闭爬虫




        # nodelist = response.xpath('//div[@class="col2_right j_threadlist_li_right "]')#得到一页中的所有帖子
        # print(nodelist)
        # item = BaiduspiderItem()
        # isHasContent = False  # 判断此页中是否有合适的信息
        # NextPageUrl = ''
        # for node in nodelist:#分析帖子信息
        #     item["title"]= node.xpath("./div[1]/div/a[@title]/text()").extract_first()
        #     item["url"] = node.xpath("./div[1]/div/a[@href]/@href").extract_first()
        #     item["info"] = node.xpath('./div[2]/div[@class="threadlist_text pull_left"]/div[1]/text()').extract_first()
        #     item["time"] = node.xpath('./div[1]/div[2]/span[@title="创建时间"]/text()').extract_first()
        #     item["time"] = item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
        #     # 判断一页中是否有符合年限的帖子
        #     if(isHasContent == False):
        #         isHasContent = TimeMarch.time_March(item["time"],self.default_scope_day)
        #     # 判断这个帖子是否符合时间
        #     if(TimeMarch.time_March(item["time"],self.default_scope_day)==True):
        #         item["IsFilter"] = True
        #     else:
        #         item["IsFilter"] = False
        #     # 拼接子url
        #     childUrl = "https://tieba.baidu.com" + item["url"]
        #     item["url"] = childUrl
        #     item["urlId"] = item['url'].split('/')[4] #得到urlId
        #     item["urlId"] = '%s_%s'%(self.name,item["urlId"])
        #     childUrl = item["url"]
        #     res_child = child_page(childUrl)
        #     item["comment"] = res_child.xpath("//div[@id='thread_theme_5']/div[1]/ul/li[2]/span[1]/text()")
        #     # 处理简介为空的情况
        #     if item["info"] == None:
        #         item["info"]= ''
        #     else:
        #         item["info"]=item["info"].strip()#将多余空格去掉
        #     item["time"] = item["time"].strip()
        #     try:
        #         if (NextPageUrl == ''):  # 记录下一页的链接
        #             NextPageUrl = 'https:' + response.xpath('//a[@class = "next pagination-item "]/@href').extract_first()
        #     except:
        #         url = response.url
        #         print("url is :----------"+url)
        #         temp = url.split("kw=")[1]
        #         if ("page" not in url):
        #             NextPageUrl = "https://tieba.baidu.com/f?kw=" + keyword + "&ie=utf-8&pn=50"
        #         else:
        #             page = temp.split("pn=")[1]
        #             page = int(page)+50
        #             NextPageUrl = "https://tieba.baidu.com/f?kw=" + keyword + "&ie=utf-8&pn="+str(page)
        #
        #     yield item #返回数据到pipeline
        # if(isHasContent==False):#根据判断决定继续爬取还是结束
        #      self.crawler.engine.close_spider(self, 'Finished')#关闭爬虫
        # else:
        #     yield scrapy.Request(NextPageUrl,callback = self.parse,dont_filter=True)
        #     print("翻页了！！！！！！！！！！！！！！！！！\n\n\n")
