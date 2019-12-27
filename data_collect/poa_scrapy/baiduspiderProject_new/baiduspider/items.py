# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # 标题
    title = scrapy.Field()
    # 内容
    info = scrapy.Field()
    # 时间
    time = scrapy.Field()
    # 网址
    url = scrapy.Field()
    # 帖子id
    urlId = scrapy.Field()
    # 是否符合条件（包括时间范围）
    IsFilter = scrapy.Field()
    # 评论数
    comment = scrapy.Field()
    # 阅读数
    read = scrapy.Field()
    # 点赞数
    like = scrapy.Field()
    # 爬取时间
    spidertime = scrapy.Field()
    # 最新评论时间
    latestcomtime = scrapy.Field()
    # 来源
    source = scrapy.Field()

def inititem(item):
    item['title'] = None
    item['info'] = None
    item['time'] = None
    item['url'] = None
    item['urlId'] = None
    item['IsFilter'] = None
    item['comment'] = None
    item['read'] = None
    item['like'] = None
    item['spidertime'] = None
    item['latestcomtime'] = None
    item['source'] = None
    return item


