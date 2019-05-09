#!/usr/bin/env python
# coding=utf-8

import time
import schedule

from aio_proxy_pool.config import CRAWLER_RUN_CYCLE, VALIDATOR_RUN_CYCLE

from aio_proxy_pool.spiders import Crawler
from aio_proxy_pool.validator import Validator
from aio_proxy_pool.logger import logger


def run_schedule():
    """
    启动客户端
    """
    # 启动收集器
    schedule.every(CRAWLER_RUN_CYCLE).minutes.do(Crawler.run).run()
    # 启动验证器
    schedule.every(VALIDATOR_RUN_CYCLE).minutes.do(Validator.run).run()

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("You have canceled all jobs")
            return
