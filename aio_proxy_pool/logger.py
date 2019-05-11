#!/usr/bin/env python
# coding=utf-8
import os
import logging
import logging.config as log_conf
import datetime
import coloredlogs

log_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/logs'
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
today = datetime.datetime.now().strftime("%Y%m%d")

log_path = os.path.join(log_dir, f'{today}.log')

log_config = {
    'version': 1.0,
    'disable_existing_loggers': False,
    'formatters': {
        'colored_console': {'()': 'coloredlogs.ColoredFormatter',
                            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 'datefmt': '%H:%M:%S'},
        'detail': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"  # 如果不加这个会显示到毫秒。
        },
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',  # 日志打印到屏幕显示的类。
            'level': 'DEBUG',
            'formatter': 'colored_console'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',  # 日志打印到文件的类。
            'maxBytes': 1024 * 1024 * 1024,  # 单个文件最大内存
            'backupCount': 1,  # 备份的文件个数
            'filename': log_path,  # 日志文件名
            'level': 'INFO',  # 日志等级
            'formatter': 'detail',  # 调用上面的哪个格式
            'encoding': 'utf-8',  # 编码
        },
    },
    'loggers': {
        'aio_proxy_pool': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False  # log是否向父级log传播
        }
    }
}

log_conf.dictConfig(log_config)
logger = logging.getLogger('aio_proxy_pool')
