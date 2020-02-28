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
    SQLIte数据库最大支持128TiB(140 terabytes, or 128 tebibytes, or 140,000 gigabytes or 128,000 gibibytes).
    """

    def open_spider(self, spider):
        """
        当spider被开启的时候调用这个方法
        """
        # 1). 创建数据库表；
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
            tags varchar(200),
            status int);
        """
        # 2). 将创建数据库表的结果存储到日志便于测试与排错。
        try:
            self.cursor.execute(create_sql)
        except Exception as e:
            logging.error("Connect sqlite failed" + str(e))
        else:
            logging.info("Connect sqlite successful")

    def process_item(self, item, spider):
        # 0). 基于colorama模块显示字体, 初始化字体颜色
        colorama.init()

        # 1). 添加新的产品信息到数据库中；
        # Add product to database if it's unique
        insert_sql = """
            insert into products_shopify 
            (name, description, image, link, price, stock, tags, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            item = dict(item)
            if item.get('stock'):
                self.cursor.execute(insert_sql, (item.get('name', ''),
                                                 item.get('description', ''),
                                                 item.get('image', ''),
                                                 item.get('link', ''),
                                                 item.get('price', ''),
                                                 item.get('stock', 0),
                                                 item.get('tags', ''),
                                                 1))  # 1代表商品状态为上新
                self.conn.commit()

        # 2). 如果添加产品到数据库失败，则表明不是新产品，判断价格和库存是否变化。
        except sqlite3.IntegrityError as e:
            # 根据库存判断商品是否售罄；
            # 根据库存判断商品是否售罄；
            if item['stock']:
                select_sql = """
                SELECT  price, stock 
                FROM products_shopify 
                WHERE link=?;
                """
                # 单个元素的元组必须加逗号。
                self.cursor.execute(select_sql, (item['link'], ))
                db_prices, db_stock = self.cursor.fetchone()
                db_stock = int(db_stock)
                spider_stock = int(item['stock'])
                if db_stock < spider_stock:  # 库存数小于新爬取商品数量，说明产品补货 2-补货
                    update_sql = """
                        UPDATE  products_shopify 
                        SET status=2, price=?,stock=? 
                        WHERE link=?;
                    """
                    self.cursor.execute(update_sql, (item.get('price', ''), item['stock'], item['link']))
                    self.conn.commit()
                    # todo: Find Stock is change? If YES, send to discord
                    logging.info("Product <%s> is restocking, the restock count is %s" % (item['name'], item['stock'] - db_stock))
                    print(Fore.LIGHTBLUE_EX + "Product <%s> is restocking, the restock count is %s" % (
                        item['name'], item['stock'] - db_stock))
            else:
                # status=3代表商品售罄
                update_sql = "UPDATE  products_shopify SET status=3, price='',stock=0 WHERE link=?;"
                self.cursor.execute(update_sql, (item['link'], ))
                self.conn.commit()
                logging.info("Product <%s> already sold out." % (item['name']))
                print(Fore.RED + "Product <%s> already sold out." % (item['name']))

        except Exception as e:
            logging.error('Insert item data into sqlite error.' + str(e))
        # 3). 如果添加产品成功，说明是一个新产品。
        else:
            # todo: New Project? If YES, send to discord.
            logging.info("Found new product <%s>." % (item["name"]))
            print(Fore.GREEN + "Found new product <%s>." % (item["name"]))

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
