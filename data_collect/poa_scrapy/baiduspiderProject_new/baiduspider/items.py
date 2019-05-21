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
