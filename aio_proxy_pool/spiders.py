#!/usr/bin/env python
# coding=utf-8
import asyncio
import re

import pyquery

import os
import sys



base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,base_dir)

from utils import fetch
from database import RedisClient
from logger import logger
from config import loop
from config import HEADERS

redis_conn = RedisClient()
all_funcs = []


def collect_funcs(func):
    """
    装饰器，用于收集爬虫函数
    """
    all_funcs.append(func)
    return func


class Crawler:
    @staticmethod
    def run():
        """
        启动收集器
        """
        logger.info("Crawler working...")
        tasks = []
        for func in all_funcs:
            for proxy in func():
                if proxy:
                    tasks.append(asyncio.ensure_future(redis_conn.add_proxy(proxy)))
                    logger.info("Crawler {} √ {}".format(func.__name__,proxy))

        loop.run_until_complete(asyncio.wait(tasks))
        logger.info("Crawler resting...")



    @staticmethod
    @collect_funcs
    def quanwangdaili():
        """
        全网代理：http://www.goubanjia.com/
        """
        url = "http://www.goubanjia.com/"
        html = fetch(url)

        if html:
            doc = pyquery.PyQuery(html)
            proxy_ips = doc(".table-hover td.ip").items()
            proxy_schemes = doc('td:nth-child(3)').items()
            for proxy_ip, proxy_scheme in zip(proxy_ips, proxy_schemes):
                scheme = proxy_scheme('a.href').text()
                port = proxy_ip(".port").attr("class")
                # 位运算向右移动3 也就是十进制除以8
                port_number = int("".join([str("ABCDEFGHIZ".index(_)) for _ in port.split()[1]])) >> 3
                proxy_ip.find('.port').remove()
                proxy_ip.find('[style*="none;"]').remove()
                yield (scheme + "://" + "".join(proxy_ip.text().replace(" ", "").split("\n")) + str(port_number))

    @staticmethod
    @collect_funcs
    def kuaidaili():
        """
        快代理：https://www.kuaidaili.com
        """
        url = "https://www.kuaidaili.com/free/{}"
        items = ["inha/{}/".format(_) for _ in range(1,21)]
        for proxy_type in items:
            html = fetch(url.format(proxy_type))
            if html:
                doc = pyquery.PyQuery(html)
                for proxy in doc(".table-bordered tr").items():
                    ip = proxy("[data-title=IP]").text()
                    port = proxy("[data-title=PORT]").text()
                    if ip and port:
                        yield "http://{}:{}".format(ip, port)

    @staticmethod
    @collect_funcs
    def ip3366():
        """
        云代理：http://www.ip3366.net
        """
        url = "http://www.ip3366.net/free/?stype=1&page={}"

        items = [p for p in range(1, 8)]
        for page in items:
            html = fetch(url.format(page))
            if html:
                doc = pyquery.PyQuery(html)
                for proxy in doc(".table-bordered tr").items():
                    ip = proxy("td:nth-child(1)").text()
                    port = proxy("td:nth-child(2)").text()
                    schema = proxy("td:nth-child(4)").text()
                    if ip and port and schema:
                        yield "{}://{}:{}".format(schema.lower(), ip, port)
    #
    @staticmethod
    @collect_funcs
    def data5u():
        """
        无忧代理：http://www.data5u.com/
        """
        url = "http://www.data5u.com/"

        html = fetch(url)
        if html:
            doc = pyquery.PyQuery(html)
            for index, item in enumerate(doc("li ul").items()):
                if index > 0:
                    ip = item("span:nth-child(1)").text()
                    port = item("span:nth-child(2)").text()
                    schema = item("span:nth-child(4)").text()
                    if ip and port and schema:
                        yield "{}://{}:{}".format(schema, ip, port)
    #
    @staticmethod
    @collect_funcs
    def iphai():
        """
        ip 海代理：http://www.iphai.com
        """
        url = "http://www.iphai.com/free/{}"

        items = ["ng"]
        for proxy_type in items:
            html = fetch(url.format(proxy_type))
            if html:
                doc = pyquery.PyQuery(html)
                for item in doc(".table-bordered tr").items():
                    ip = item("td:nth-child(1)").text()
                    port = item("td:nth-child(2)").text()
                    schema = item("td:nth-child(4)").text()
                    if not schema:
                        schema = "HTTP"
                    if ip and port and schema:
                        yield "{}://{}:{}".format(schema.lower(), ip, port)

    @staticmethod
    @collect_funcs
    def ip89():
        """
        89免费代理：http://http://www.89ip.cn
        """
        url = "http://www.89ip.cn/index_{}.html"

        items = [p for p in range(1, 8)]
        for proxy_type in items:
            html = fetch(url.format(proxy_type))
            if html:
                doc = pyquery.PyQuery(html)
                for item in doc(".layui-col-md8 tr").items():
                    ip = item("td:nth-child(1)").text()
                    port = item("td:nth-child(2)").text()
                    if ip and port:
                        yield "http://{}:{}".format(ip, port)
                        yield "https://{}:{}".format(ip, port)

    @staticmethod
    @collect_funcs
    def ip_66():
        """
        66ip 代理：http://www.66ip.cn
        """
        from copy import deepcopy
        headers = deepcopy(HEADERS)
        headers.update({"Cookie":"__jsluid=b93d68c70282ececa5ac51068667d250; __jsl_clearance=1557549794.546|0|ZphsoSMFkHToyzuKEf5o9ht1b2M%3D"})
        url = 'http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=1&proxytype={}&api=66ip'
        pattern = "\d+\.\d+.\d+\.\d+:\d+"
        items = [(0, "http://{}"), (1, "https://{}")]
        for item in items:
            proxy_type, host = item
            html = fetch(url.format(proxy_type),headers=headers)
            if html:
                for proxy in re.findall(pattern, html):
                    yield host.format(proxy)

    @staticmethod
    @collect_funcs
    def xici():
        """
        西刺代理：http://www.xicidaili.com
        """
        url = "http://www.xicidaili.com/{}"

        items = []
        for page in range(1, 21):
            items.append(("wt/{}".format(page), "http://{}:{}"))
            items.append(("wn/{}".format(page), "https://{}:{}"))

        for item in items:
            proxy_type, host = item
            html = fetch(url.format(proxy_type))
            if html:
                doc = pyquery.PyQuery(html)
                for proxy in doc("table tr").items():
                    ip = proxy("td:nth-child(2)").text()
                    port = proxy("td:nth-child(3)").text()
                    if ip and port:
                        yield host.format(ip, port)

Crawler.run()