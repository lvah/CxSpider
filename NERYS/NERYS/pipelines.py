# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import sqlite3
import colorama
from colorama import Fore


class NerysPipeline(object):
    def process_item(self, item, spider):
        return


class SqlitePipeline(object):
    """
    将item写入sqlite,默认是products.db文件
    """

    def open_spider(self, spider):
        """当spider被开启的时候调用这个方法"""
        db_name = 'products.db'
        # Create database
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        create_sql = """
        CREATE TABLE IF NOT EXISTS products_shopify(
            name varchar(100),
            description varchar(200), 
            image varchar(200),
            link varchar(200) unique , 
            price float default  null, 
            stock int default 0, 
            tags varchar(200));
        """
        try:
            self.cursor.execute(create_sql)
        except Exception as e:
            logging.error("Connect sqlite failed" + str(e))
        else:
            logging.info("Connect sqlite successful")

    def process_item(self, item, spider):
        # 初始化字体颜色
        colorama.init()
        # Add product to database if it's unique
        insert_sql = """
            insert into products_shopify 
            (name, description, image, link, price, stock, tags) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        try:
            item = dict(item)
            self.cursor.execute(insert_sql, (item.get('name', ''),
                                             item.get('description', ''),
                                             item.get('image', ''),
                                             item.get('link', ''),
                                             item.get('price', ''),
                                             item.get('stock', 0),
                                             item.get('tags', '')))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            logging.info("Product <%s> already exists in the database." % (item['name']))
            print(Fore.BLUE + "Product <%s> already exists in the database." % (item['name']))
            select_sql = "select price, stock from products_shopify where link='%s'" % (item['link'])
            self.cursor.execute(select_sql)
            prices, stock = self.cursor.fetchone()
            # todo: Find Price is change? If Yes, send to discord
            pass

            # todo: Find Stock is change? If YES, send to discord
            # If new stock is bigger than database stock, So this site restock。
            if item.get('stock', 0) > stock:
                # 发送通知到discord
                logging.info("Restock: product <%s> add <%s> today" % (item['name'], item.get('stock', 0) - stock))


        except Exception as e:
            logging.error('Insert item data into sqlite error.' + str(e))
        else:
            # todo: New Project? If YES, send to discord.
            logging.info("Found new product <%s>." % (item["name"]))
            print(Fore.GREEN + "Found new product <%s>." % (item["name"]))

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
