# Description
Develop the fastest Shopify monitor / scraper. The monitor can run 24/7 on a web server and could be able to handle 70+ Shopify sites simultaneously. The scraper  push each restock or newly added product to a Discord webhook. The newly added product or restock will be pushed in a format that contains a direct ATC link for each size, image, and stock quantity.


# Project Directory

```
─NERYS
    └─NERYS
        ├─doc           # 配置shopify网址和关键字的文件
        ├─log           # 日志文件
        ├─spiders       # 爬虫，项目核心代码
          ├─shopify.py
        ├─item.py       # 数据库存储对象 
        ├─middlewares.py     
        ├─pipeline.py   # 数据存储，此代码使用sqlite，可修改为mysql，mongodb等。 
        ├─main.py       # 定时任务代码，每隔5秒自动爬取(主程序代码) 

```


# Quick Use

```bash
# 进入cd CXProject/NERYS/NERYS目录， 执行命令如下速度更快
scrapy crawl shopify
```
