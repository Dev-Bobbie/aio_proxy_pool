#!/usr/bin/env python
# coding=utf-8

# gunicorn config
# gunicorn -c aio_proxy_pool/gunicorn.py --worker-class sanic.worker.GunicornWorker aio_proxy_pool.webapi_sanic:app

bind = '0.0.0.0:8001'
backlog = 2048

workers = 4
worker_connections = 1000
timeout = 30
keepalive = 2

spew = False
daemon = False
umask = 0