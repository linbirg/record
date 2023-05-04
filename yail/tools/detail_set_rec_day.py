#!/usr/bin/python3
# -*- coding:utf-8 -*-
# Author: yizr

import os
import sys

__abs_file__ = os.path.abspath(__file__)
tool_dir = os.path.dirname(__abs_file__)
code_dir = os.path.dirname(tool_dir)
sys.path.append(code_dir)


import asyncio
from lib.yom import Pool
from www.dao.week_note import Detail

from utils.date_util import DateHelper

@asyncio.coroutine
def init_pool(loop):
    pool = yield from Pool.create_pool(loop=loop,
                                    host='127.0.0.1',
                                    port=3306,
                                    user='record',
                                    password='ww123456',
                                    db='record')

    return pool

    


@asyncio.coroutine
def handle_detail(detail):
    rec_day = DateHelper.to_date(detail.created_at)
    print(rec_day)
    detail.rec_date = rec_day

    yield from detail.update()


@asyncio.coroutine
def handler():
    details = yield from Detail.find_all()
    for dt in details:
        yield from handle_detail(dt)

@asyncio.coroutine
def start(loop):
    yield from init_pool(loop)
    yield from handler()


if __name__ == '__main__':
    __loop = asyncio.get_event_loop()
    __loop.run_until_complete(start(__loop))