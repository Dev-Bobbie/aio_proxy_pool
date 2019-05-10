#!/usr/bin/env python
# coding=utf-8

import random

import aioredis
import os
import sys

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,base_dir)
from utils import dec_connector

from config import (
    REDIS_KEY,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_HOST,
    REDIS_MAX_CONNECTION,
    REDIS_MIN_CONNECTION,
    MAX_SCORE,
    MIN_SCORE,
    INIT_SCORE,
    DB
)


class RedisClient:
    """
    代理池依赖了 Redis 数据库，使用了其`有序集合`的数据结构
    （可按分数排序，key 值不能重复）
    """
    _db = {}
    redis = None

    def __init__(self, host=REDIS_HOST,db=DB, port=REDIS_PORT, password=REDIS_PASSWORD):
        self.host = host
        self.port = port
        self.db = db
        self.password = password

    @dec_connector
    async def add_proxy(self, proxy, score=INIT_SCORE):
        """
        新增一个代理，初始化分数 INIT_SCORE < MAX_SCORE，确保在
        运行完收集器后还没运行校验器就获取代理，导致获取到分数虽为 MAX_SCORE,
        但实际上确是未经验证，不可用的代理

        :param proxy: 新增代理
        :param score: 初始化分数
        """
        if not await self.redis.zscore(REDIS_KEY, proxy):
            await self.redis.zadd(REDIS_KEY,int(score),proxy)

    @dec_connector
    async def reduce_proxy_score(self, proxy):
        """
        验证未通过，分数减一

        :param proxy: 验证代理
        """
        score = await self.redis.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            await self.redis.zincrby(REDIS_KEY,-1,proxy)
        else:
            await self.redis.zrem(REDIS_KEY, proxy)

    @dec_connector
    async def increase_proxy_score(self, proxy):
        """
        验证通过，分数加一

        :param proxy: 验证代理
        """
        score = await self.redis.zscore(REDIS_KEY, proxy)
        if score and score < MAX_SCORE:
            await self.redis.zincrby(REDIS_KEY,1,proxy)

    @dec_connector
    async def pop_proxy(self):
        """
        返回一个代理
        """
        # 第一次尝试取分数最高，也就是最新可用的代理
        first_chance = await self.redis.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if first_chance:
            return random.choice(first_chance)

        else:
            # 第二次尝试取 7-10 分数的任意一个代理
            second_chance = await self.redis.zrangebyscore(
                REDIS_KEY, MAX_SCORE - 3, MAX_SCORE
            )
            if second_chance:
                return random.choice(second_chance)
            # 最后一次就随便取咯
            else:
                last_chance = await self.redis.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
                if last_chance:
                    return random.choice(last_chance)

    @dec_connector
    async def get_proxies(self, count=1):
        """
        返回指定数量代理，分数由高到低排序

        :param count: 代理数量
        """
        proxies = await self.redis.zrevrange(REDIS_KEY, 0, int(count) - 1)
        return [proxy.decode("utf-8") for proxy in proxies]

    @dec_connector
    async def count_all_proxies(self):
        """
        返回所有代理总数
        """
        return await self.redis.zcard(REDIS_KEY)

    @dec_connector
    async def count_score_proxies(self, score):
        """
        返回指定分数代理总数

        :param score: 代理分数
        """
        if 0 <= int(score) <= 10:
            proxies = await self.redis.zrangebyscore(REDIS_KEY, int(score), int(score))
            return len(proxies)
        return -1

    @dec_connector
    async def clear_proxies(self, score):
        """
        删除分数小于等于 score 的代理
        """
        if 0 <= int(score) <= 10:
            proxies = await self.redis.zrangebyscore(REDIS_KEY, 0, int(score))
            for proxy in proxies:
                await self.redis.zrem(REDIS_KEY, proxy)
            return True
        return False


    @dec_connector
    async def all_proxies(self):
        """
        返回全部代理
        """
        return await self.redis.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)


    async def _db_client(self, db=None):
        client = await aioredis.create_redis_pool(
            'redis://{host}:{port}/{db}'.format(host=self.host, port=self.port,db=db),
            password=self.password,
            minsize=REDIS_MIN_CONNECTION,
            maxsize=REDIS_MAX_CONNECTION)
        return client

    async def _connector(self, db=None):
        if db is None:
            db = self.db
        if db not in self._db:
            self._db[db] = self.redis = await self._db_client(db)
        return self._db[db]

