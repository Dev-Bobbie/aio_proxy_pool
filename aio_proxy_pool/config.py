#!/usr/bin/env python
# coding=utf-8
import asyncio
# 请求超时时间（秒）
import os

REQUEST_TIMEOUT = 5
# 请求延迟时间（秒）
REQUEST_DELAY = 0

# redis 地址
REDIS_HOST = "redis"
# redis 端口
REDIS_PORT = 6399
# redis 密码
REDIS_PASSWORD = None
# redis set key
REDIS_KEY = "async_pool:proxies"
# redis 连接池最大连接量
REDIS_MAX_CONNECTION = 10
REDIS_MIN_CONNECTION = 5
DB = 0

# REDIS SCORE 最大分数
MAX_SCORE = 10
# REDIS SCORE 最小分数
MIN_SCORE = 0
# REDIS SCORE 初始分数
INIT_SCORE = 9

# 批量测试数量
VALIDATOR_BATCH_COUNT = 256
# 校验器测试网站，可以定向改为自己想爬取的网站，如新浪，知乎等
VALIDATOR_BASE_URL = "http://baidu.com"
# 校验器循环周期（分钟）
VALIDATOR_RUN_CYCLE = 5

# 爬取器循环周期（分钟）
CRAWLER_RUN_CYCLE = 30
# 请求 headers
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
}

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

loop = asyncio.get_event_loop()
