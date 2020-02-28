# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NerysItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()               # 商品名称
    description = scrapy.Field()        # 商品描述
    image = scrapy.Field()              # 商品图片地址
    link = scrapy.Field()               # 商品购买链接
    price = scrapy.Field()              # 商品价格
    stock = scrapy.Field()              # 商品库存量
    tags= scrapy.Field()                # 商品标签
    status = scrapy.Field()             # 商品状态: 1-上新，2-补货，3-售罄
