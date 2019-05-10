FROM python:3.6
MAINTAINER bobbie <dev.bobbie@gmail.com>

COPY ./aio_proxy_pool /code/aio_proxy_pool

WORKDIR /code/aio_proxy_pool
# 安装依赖
RUN pip install --no-cache-dir --trusted-host mirrors.aliyun.com -i http://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY run.py /code/

ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime