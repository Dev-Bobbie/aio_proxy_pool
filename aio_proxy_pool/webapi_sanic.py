#!/usr/bin/env python
# coding=utf-8

from sanic import Sanic
from sanic.response import json,html
import os
import sys

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,base_dir)

from database import RedisClient

app = Sanic()
redis_conn = RedisClient()


@app.route("/")
async def index(request):
    return html('<h2>Welcome to Proxy Pool System</h2>')


@app.route("/pop")
async def pop_proxy(request):
    proxy = await redis_conn.pop_proxy()
    if proxy:
        proxy = proxy.decode('utf-8')
    if proxy[:5] == "https":
        return json({"https": proxy})
    else:
        return json({"http": proxy})


@app.route("/get/<count>")
async def get_proxy(request, count):
    res = []
    for proxy in await redis_conn.get_proxies(count):
        if proxy[:5] == "https":
            res.append({"https": proxy})
        else:
            res.append({"http": proxy})
    return json(res)


@app.route("/count")
async def count_all_proxies(request):
    count = await redis_conn.count_all_proxies()
    return json({"count": str(count)})


@app.route("/count/<score>")
async def count_score_proxies(request, score):
    count = await redis_conn.count_score_proxies(score)
    return json({"count": str(count)})


@app.route("/clear/<score>")
async def clear_proxies(request, score):
    if await redis_conn.clear_proxies(score):
        return json({"Clear": "Successful"})
    return json({"Clear": "Score should >= 0 and <= 10"})


app.run(host='0.0.0.0')