#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'linbirg'
'''
async web application.
在廖老师的web框架基础上修改而来，感谢廖老师。
'''

import logging
logging.basicConfig(level=logging.INFO)

# import asyncio, time
# from datetime import datetime

# from jinja2 import Environment, FileSystemLoader

# from conf import db as dbconf

# from lib.yeab.web import add_routes, add_static

from www.filters.filters import cors

from lib.yeab.yeab import Yeab


if __name__ == "__main__":
    app = Yeab(filters_pkg='www.filters')
    app.after_request(cors)
    app.run()