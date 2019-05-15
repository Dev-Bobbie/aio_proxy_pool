#!/usr/bin/env python
# coding=utf-8

import asyncio
import aiohttp

import os
import sys

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
from config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY
from config import loop


async def _get_page(url, sleep, headers):
    """
    获取并返回网页内容
    """
    async with aiohttp.ClientSession() as session:
        try:
            await asyncio.sleep(sleep)
            async with session.get(
                    url, headers=headers, timeout=REQUEST_TIMEOUT
            ) as resp:
                return await resp.text()
        except:
            return ""


def fetch(url, sleep=REQUEST_DELAY, headers=HEADERS):
    """
    请求方法，用于获取网页内容

    :param url: 请求链接
    :param sleep: 延迟时间（秒）
    """
    html = loop.run_until_complete(_get_page(url, sleep, headers=headers))
    if html:
        return html


from functools import wraps


def dec_connector(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.redis is None:
            self.redis = await self._connector()

        return await func(self, *args, **kwargs)

    return wrapper

import requests
import execjs

def fetch_66_cookie():
    """
    获取 cookies
    :return:
    """
    cookie_url = 'http://www.66ip.cn/'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
    }
    while True:
        response = requests.get(cookie_url, headers=headers)
        js_code1 = response.text
        js_code1 = js_code1.rstrip('\n')
        js_code1 = js_code1.replace('</script>', '')
        js_code1 = js_code1.replace('<script>', '')
        index = js_code1.rfind('}')
        js_code1 = js_code1[0:index + 1]
        js_code1 = 'function getCookie() {' + js_code1 + '}'
        js_code1 = js_code1.replace('eval', 'return')

        js_code2 = execjs.compile(js_code1)
        code = js_code2.call('getCookie')
        if 'document.cookie' in code:
            break

    code = 'var a' + code.split('document.cookie')[1].split("Path=/;'")[0] + "Path=/;';return a;"
    code = 'window = {}; \n' + code
    js_final = "function getClearance(){" + code + "};"
    js_final = js_final.replace("return return", "return eval")
    ctx = execjs.compile(js_final)
    jsl_clearance = ctx.call('getClearance')

    jsl_uid = response.headers["Set-Cookie"].split(";")[0]
    jsl_cle = jsl_clearance.split(';')[0].split('=')[1]
    cookie = f"{jsl_uid}; __jsl_clearance={jsl_cle}"
    return cookie


async def get_cookie():
    return await loop.run_in_executor(None,fetch_66_cookie)
