"""
FileName: main
Date: 22 15
Author: lvah
Connect: 976131979@qq.com
Description:

定时爬虫任务

"""
import subprocess
import time

import  apscheduler
# 轻量级的定时任务调度的库：schedule。
import  schedule

def crawl_work():
    # Execute a child program in a new process.
    subprocess.Popen('scrapy crawl shopify')

if __name__=='__main__':
    schedule.every(5).minutes.do(crawl_work)
    while True:
        schedule.run_pending()
        time.sleep(1)
