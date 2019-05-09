#!/usr/bin/env python
# coding=utf-8

import asyncio
import aiohttp

from aio_proxy_pool.config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

loop = asyncio.get_event_loop()


async def _get_page(url, sleep):
    """
    获取并返回网页内容
    """
    async with aiohttp.ClientSession() as session:
        try:
            await asyncio.sleep(sleep)
            async with session.get(
                url, headers=HEADERS, timeout=REQUEST_TIMEOUT
            ) as resp:
                return await resp.text()
        except:
            return ""


def fetch(url, sleep=REQUEST_DELAY):
    """
    请求方法，用于获取网页内容

    :param url: 请求链接
    :param sleep: 延迟时间（秒）
    """

    html = loop.run_until_complete(_get_page(url, sleep))
    return html



from functools import wraps

def dec_connector(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.redis is None:
            self.redis = await self._connector()

        return await func(self, *args, **kwargs)

    return wrapper
