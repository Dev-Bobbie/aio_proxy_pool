#!/usr/bin/env python
# coding=utf-8

import os
import asyncio
import aiohttp

import os
import sys

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from config import VALIDATOR_BASE_URL, VALIDATOR_BATCH_COUNT, REQUEST_TIMEOUT
from logger import logger
from database import RedisClient
from config import loop

VALIDATOR_BASE_URL = os.environ.get("VALIDATOR_BASE_URL") or VALIDATOR_BASE_URL


class Validator:
    def __init__(self):
        self.redis = RedisClient()

    async def test_proxy(self, proxy):
        """
        测试代理

        :param proxy: 指定代理
        """
        async with aiohttp.ClientSession() as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf8")
                async with session.get(
                        VALIDATOR_BASE_URL, proxy=proxy, timeout=REQUEST_TIMEOUT
                ) as resp:
                    if resp.status == 200:
                        await self.redis.increase_proxy_score(proxy)
                        logger.info("Validator √ {}".format(proxy))
                    else:
                        await self.redis.reduce_proxy_score(proxy)
                        logger.info("Validator × {}".format(proxy))
            except:
                await self.redis.reduce_proxy_score(proxy)
                logger.info("Validator × {}".format(proxy))

    async def main(self):
        """
        启动校验器
        """
        logger.info("Validator working...")
        logger.info("Validator website is {}".format(VALIDATOR_BASE_URL))

        proxies = await self.redis.all_proxies()
        for i in range(0, len(proxies), VALIDATOR_BATCH_COUNT):
            _proxies = proxies[i: i + VALIDATOR_BATCH_COUNT]
            for proxy in _proxies:
                if proxy:
                    await asyncio.ensure_future(self.test_proxy(proxy))

        logger.info("Validator resting...")

    @staticmethod
    def run():
        validator = Validator().main()
        loop.run_until_complete(validator)

# Validator.run()
