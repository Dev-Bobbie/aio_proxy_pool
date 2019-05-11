#!/usr/bin/env python
# coding=utf-8
import subprocess

if __name__ == '__main__':
    servers = [
        ["gunicorn", "-c", "aio_proxy_pool/gunicorn.py", "--worker-class",
         "sanic.worker.GunicornWorker", 'aio_proxy_pool.webapi_sanic:app'],
        ["python", "aio_proxy_pool/scheduler.py"]
    ]
    procs = []
    for server in servers:
        proc = subprocess.Popen(server)
        procs.append(proc)
    for proc in procs:
        proc.wait()
        if proc.poll():
            exit(0)
