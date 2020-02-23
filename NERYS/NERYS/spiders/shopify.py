# -*- coding: utf-8 -*-
import copy
import json
import logging
import re

import scrapy
from colorama import Fore
from scrapy import Request

from NERYS.items import NerysItem


class ShopifySpider(scrapy.Spider):
    name = 'shopify'
    # allowed_domains = ['deadstock.ca']
    start_urls = [
        # 'https://www.deadstock.ca/collections/all/products.atom',
        # 'https://www.notre-shop.com/collections/all/products.atom',
        'https://ca.octobersveryown.com/collections/all/products.atom',
        'https://www.bdgastore.com/collections/all/products.atom',

    ]

    def start_requests(self):
        # 1). 加载关键字
        with open('doc/keywords.txt') as f:
            self.keywords = [keyword.strip() for keyword in f]
        # 2). 加载shopify网址并预处理
        with open('doc/shopify-sites.txt') as f:
            urls = [url.strip() + '/collections/all/products.atom' for url in f]
        # 3). 爬取加载的所有shopify网址，并调用parse函数解析页面内容。
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        # 1). 实例化Item对象，存储商品信息。
        item = NerysItem()
        # 2). 对shopify网站响应内容做xpath处理。
        content = response.text.encode('utf-8')
        from lxml import etree
        html = etree.HTML(content)

        # 3). 基于xpath语法解析商品信息
        # Get products with the specified keywords
        products_raw = html.xpath('//entry')

        for product in products_raw:
            title = product.xpath("./title/text()")[0]
            # Get the product info
            item['name'] = title
            item['link'] = product.xpath("./link/@href")[0]
            item['image'] = product.xpath(".//tr/td/img/@src")[0]
            # 4). 加载商品详情页并通过detail_parse解析页面信息， item对象必须深拷贝(参考深拷贝和浅拷贝的区别)
            yield Request(url=item['link'] + '.json',
                          meta={'item': copy.deepcopy(item)},
                          callback=self.detail_parse)

    def detail_parse(self, response):
        # 1). 获取传递的meta数据。
        item = response.meta['item']
        # 2). 解析响应的json数据
        json_content = json.loads(response.text)
        # 3). 基于字典的key-value解析商品的详细信息
        # todo: Get Product Stock
        product = json_content.get('product')
        if product:
            # 默认获取的商品描述时html标签， 基于正则表达式删除标签，只留下文本信息。
            no_tag_pattern = re.compile(r'<.*?>')
            description = re.sub(no_tag_pattern, '', product.get('body_html'))
            item['description'] = description.replace('\n', '').strip()
            item['tags'] = product.get('tags')
            # 4). 根据商品的名称和商品标签与关键字对比， 筛选出需要的商品信息并返回。
            # Check if the keywords are in the product's name or tags
            product_found = False
            for keyword in self.keywords:
                keyword = keyword.strip()
                if keyword.upper() in item['name'].upper() or keyword.upper() in item['tags'].upper():
                    logging.info("Find keyword <%s> in product <%s>" %(keyword, item['name']))
                    product_found = True
                    break
            # 5). 符合筛选条件的商品信息进一步解析；
            if product_found:
                variants = {}
                for variant in product.get('variants'):
                    size = variant.get('title')
                    price = variant.get('price')
                    variants[size] = price
                item['price'] = json.dumps(variants)
                # Request 函数传递 item 时，使用的是浅复制（对象的字段值被复制时，字段引用的对象不会被复制
                return copy.deepcopy(item)
